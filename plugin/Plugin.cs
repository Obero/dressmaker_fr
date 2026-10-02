// Dressmaker - Traduction française (mod de fan, non officiel)
// Plugin BepInEx 5 : ajoute la locale "fr" et construit à la volée des tables de chaînes
// françaises à partir des tables anglaises du jeu + fr.tsv. Aucun fichier du jeu n'est modifié.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using UnityEngine;
using UnityEngine.AddressableAssets;
using UnityEngine.Localization;
using UnityEngine.Localization.Settings;
using UnityEngine.Localization.Tables;
using UnityEngine.ResourceManagement.AsyncOperations;
using UnityEngine.SceneManagement;

namespace DressmakerFR
{
    [BepInPlugin(Guid, PluginName, Version)]
    public class Plugin : BaseUnityPlugin
    {
        public const string Guid = "fr.dressmaker.localization";
        public const string PluginName = "Dressmaker FR";
        public const string Version = "1.0.0";
        public const string Code = "fr";

        internal static ManualLogSource Log;
        internal static Locale French;
        internal static Locale English;
        internal static ConfigEntry<bool> MarkUntranslated;
        ConfigEntry<bool> replaceOE;
        ConfigEntry<bool> replaceNbsp;

        // (collection, id) -> texte français
        static readonly Dictionary<string, Dictionary<long, string>> Translations =
            new Dictionary<string, Dictionary<long, string>>();

        ConfigEntry<bool> forceFrench;
        ConfigEntry<bool> testMode;
        bool sceneChecksDone;

        void Awake()
        {
            Log = Logger;
            forceFrench = Config.Bind("General", "ForcerFrancais", true,
                "Sélectionne le français au démarrage (utile si le menu des langues ne l'affiche pas).");
            MarkUntranslated = Config.Bind("Debug", "MarquerNonTraduit", false,
                "Préfixe [EN] les chaînes pas encore traduites.");

            replaceOE = Config.Bind("Polices", "RemplacerOE", true,
                "Remplace œ/Œ par oe/Oe (les polices du jeu ne contiennent pas ce glyphe).");
            replaceNbsp = Config.Bind("Polices", "RemplacerEspaceInsecable", false,
                "Remplace l'espace insécable par une espace normale (si des carrés vides apparaissent avant : ! ?).");
            testMode = Config.Bind("Debug", "ModeTest", false,
                "Relecture en jeu : F7 = choisir une quête, F8 = choisir une chronique (au comptoir) ; " +
                "F10 / F11 = robe réussie / ratée (au mannequin). Menus de triche des développeurs, " +
                "réservés à l'éditeur Unity dans le jeu d'origine. Modifie la sauvegarde : tester sur un emplacement à part.");

            LoadTranslations();

            var sdb = LocalizationSettings.StringDatabase;
            sdb.TableProvider = new FrenchStringTableProvider(sdb.TableProvider);
            var adb = LocalizationSettings.AssetDatabase;
            adb.TableProvider = new FrenchAssetTableProvider(adb.TableProvider);

            LocalizationSettings.InitializationOperation.Completed += _ => OnLocalizationReady();
            SceneManager.sceneLoaded += OnSceneLoaded;
            Log.LogInfo($"{PluginName} {Version} chargé.");
        }

        void LoadTranslations()
        {
            var path = Path.Combine(Path.GetDirectoryName(Info.Location), "fr.tsv");
            if (!File.Exists(path))
            {
                Log.LogError($"Fichier de traduction introuvable : {path}");
                return;
            }
            int n = 0;
            foreach (var line in File.ReadAllLines(path, Encoding.UTF8))
            {
                if (line.Length == 0 || line[0] == '#') continue;
                var parts = line.Split(new[] { '\t' }, 3);
                if (parts.Length != 3 || !long.TryParse(parts[1], out var id)) continue;
                if (!Translations.TryGetValue(parts[0], out var table))
                    Translations[parts[0]] = table = new Dictionary<long, string>();
                var text = Unescape(parts[2]);
                if (replaceOE.Value) text = text.Replace("œ", "oe").Replace("Œ", "Oe");
                if (replaceNbsp.Value) text = text.Replace('\u00a0', ' ');
                table[id] = text;
                n++;
            }
            Log.LogInfo($"{n} chaînes françaises chargées ({Translations.Count} collections).");
        }

        static string Unescape(string s)
        {
            var sb = new StringBuilder(s.Length);
            for (int i = 0; i < s.Length; i++)
            {
                if (s[i] == '\\' && i + 1 < s.Length)
                {
                    char c = s[++i];
                    if (c == 'n') sb.Append('\n');
                    else if (c == 't') sb.Append('\t');
                    else if (c == '\\') sb.Append('\\');
                    else sb.Append('\\').Append(c);
                }
                else sb.Append(s[i]);
            }
            return sb.ToString();
        }

        void OnLocalizationReady()
        {
            var locales = LocalizationSettings.AvailableLocales;
            English = locales.GetLocale(new LocaleIdentifier("en"));
            if (English == null)
            {
                Log.LogError("Locale anglaise introuvable : abandon.");
                return;
            }

            French = Locale.CreateLocale(new LocaleIdentifier(Code));
            French.name = "French (fr)";
            French.LocaleName = "Français";
            locales.AddLocale(French);

            Log.LogInfo("Locales disponibles : " +
                string.Join(", ", locales.Locales.Select(l => $"{l.Identifier.Code} ({l.LocaleName})")));
            ApplyFrenchIfWanted("initialisation");
        }

        bool WantsFrench() =>
            forceFrench.Value || PlayerPrefs.GetString("selected-locale", "") == Code;

        void ApplyFrenchIfWanted(string when)
        {
            if (French == null || !WantsFrench()) return;
            if (LocalizationSettings.SelectedLocale != French)
            {
                LocalizationSettings.SelectedLocale = French;
                Log.LogInfo($"Français sélectionné ({when}).");
            }
        }

        void OnSceneLoaded(Scene scene, LoadSceneMode mode)
        {
            // Le jeu peut réimposer sa langue sauvegardée au premier chargement de scène.
            if (sceneChecksDone || French == null) return;
            sceneChecksDone = true;
            ApplyFrenchIfWanted($"scène {scene.name}");
            FontDiagnostic();
        }

        void Update()
        {
            if (!testMode.Value) return;
            if (Input.GetKeyDown(KeyCode.F7)) ShowCheatMenu("cheatQuestSelector");
            else if (Input.GetKeyDown(KeyCode.F8)) ShowCheatMenu("cheatGossipSelector");
            else if (Input.GetKeyDown(KeyCode.F10)) CallOnScene("MannequinScene", "Debug_FinishDressForceSuccess");
            else if (Input.GetKeyDown(KeyCode.F11)) CallOnScene("MannequinScene", "Debug_FinishDressForceFailure");
        }

        static Type GameType(string name) => Type.GetType(name + ", Assembly-CSharp");

        static UnityEngine.Object FindInScene(string typeName)
        {
            var t = GameType(typeName);
            if (t == null) { Log.LogWarning($"Mode test : type {typeName} introuvable."); return null; }
            var o = UnityEngine.Object.FindFirstObjectByType(t, FindObjectsInactive.Include);
            if (o == null) Log.LogWarning($"Mode test : aucun {typeName} dans la scène.");
            return o;
        }

        static void ShowCheatMenu(string field)
        {
            var desk = FindInScene("FrontDesk");
            if (desk == null) return;
            const System.Reflection.BindingFlags F =
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic;
            var menu = desk.GetType().GetField(field, F)?.GetValue(desk) as Component;
            if (menu == null) { Log.LogWarning($"Mode test : FrontDesk.{field} absent de cette version."); return; }
            menu.gameObject.SetActive(true);
            menu.GetType().GetMethod("Show")?.Invoke(menu, null);
            Log.LogInfo($"Mode test : menu {field} ouvert.");
        }

        static void CallOnScene(string typeName, string method)
        {
            var o = FindInScene(typeName);
            if (o == null) return;
            try
            {
                o.GetType().GetMethod(method)?.Invoke(o, null);
                Log.LogInfo($"Mode test : {typeName}.{method} appelé.");
            }
            catch (Exception e) { Log.LogWarning($"Mode test : {typeName}.{method} a échoué ({e.InnerException?.Message ?? e.Message})."); }
        }

        internal static StringTable BuildFrench(StringTable en, Locale locale)
        {
            var fr = ScriptableObject.CreateInstance<StringTable>();
            fr.name = en.name + "_fr";
            fr.LocaleIdentifier = locale.Identifier;
            fr.SharedData = en.SharedData;

            var collection = en.TableCollectionName;
            Translations.TryGetValue(collection, out var tr);
            int done = 0, total = 0;
            foreach (var kv in en)
            {
                total++;
                string text;
                if (tr != null && tr.TryGetValue(kv.Key, out text)) done++;
                else text = MarkUntranslated.Value ? "[EN] " + kv.Value.Value : kv.Value.Value;
                var entry = fr.AddEntry(kv.Key, text);
                entry.IsSmart = kv.Value.IsSmart;
            }
            Log.LogInfo($"Table {collection} : {done}/{total} chaînes traduites.");
            return fr;
        }

        internal static AssetTable BuildFrenchAssets(AssetTable en, Locale locale)
        {
            // Pas encore d'images traduites : on réutilise les assets anglais.
            var fr = ScriptableObject.CreateInstance<AssetTable>();
            fr.name = en.name + "_fr";
            fr.LocaleIdentifier = locale.Identifier;
            fr.SharedData = en.SharedData;
            foreach (var kv in en)
                fr.AddEntry(kv.Key, kv.Value.Address); // Address garde la sous-image « guid[nom] »
            return fr;
        }

        static void FontDiagnostic()
        {
            const string chars = "àâäçéèêëîïôöùûüÿœæÀÂÇÉÈÊËÎÏÔÙÛÜŒÆ«»\u00a0’…";
            var type = AppDomain.CurrentDomain.GetAssemblies()
                .Select(a => a.GetType("TMPro.TMP_FontAsset", false))
                .FirstOrDefault(t => t != null);
            if (type == null) { Log.LogWarning("TextMeshPro introuvable : diagnostic des polices ignoré."); return; }

            // Surcharge (texte, out manquants, chercherFallbacks, essayerAjout) : pour une police dynamique,
            // essayerAjout=true tente de générer le glyphe depuis le fichier de police source.
            var has4 = type.GetMethod("HasCharacters",
                new[] { typeof(string), typeof(List<char>).MakeByRefType(), typeof(bool), typeof(bool) });
            var has2 = type.GetMethod("HasCharacters", new[] { typeof(string), typeof(List<char>).MakeByRefType() });
            var mode = type.GetProperty("atlasPopulationMode");

            foreach (var font in Resources.FindObjectsOfTypeAll(type))
            {
                object[] args;
                bool ok;
                if (has4 != null) { args = new object[] { chars, null, false, true }; ok = (bool)has4.Invoke(font, args); }
                else if (has2 != null) { args = new object[] { chars, null }; ok = (bool)has2.Invoke(font, args); }
                else { Log.LogWarning("TMP_FontAsset.HasCharacters introuvable."); return; }

                var missing = args[1] as List<char>;
                var m = mode != null ? mode.GetValue(font, null) : "?";
                Log.LogInfo(ok
                    ? $"Police « {font.name} » [{m}] : tous les caractères français présents."
                    : $"Police « {font.name} » [{m}] : manquants [{new string(missing.ToArray()).Replace("\u00a0", "NBSP")}]");
            }
        }
    }

    class FrenchStringTableProvider : ITableProvider
    {
        readonly ITableProvider previous;
        public FrenchStringTableProvider(ITableProvider previous) { this.previous = previous; }

        public AsyncOperationHandle<TTable> ProvideTableAsync<TTable>(string tableCollectionName, Locale locale)
            where TTable : LocalizationTable
        {
            if (locale != null && locale.Identifier.Code == Plugin.Code && typeof(TTable) == typeof(StringTable))
            {
                var enHandle = LocalizationSettings.StringDatabase.GetTableAsync(tableCollectionName, Plugin.English);
                return Addressables.ResourceManager.CreateChainOperation<TTable, StringTable>(enHandle, h =>
                {
                    if (h.Status != AsyncOperationStatus.Succeeded || h.Result == null)
                        return Addressables.ResourceManager.CreateCompletedOperation<TTable>(null,
                            $"Table anglaise {tableCollectionName} introuvable");
                    return Addressables.ResourceManager.CreateCompletedOperation(
                        Plugin.BuildFrench(h.Result, locale) as TTable, null);
                });
            }
            return previous != null ? previous.ProvideTableAsync<TTable>(tableCollectionName, locale) : default;
        }
    }

    class FrenchAssetTableProvider : ITableProvider
    {
        readonly ITableProvider previous;
        public FrenchAssetTableProvider(ITableProvider previous) { this.previous = previous; }

        public AsyncOperationHandle<TTable> ProvideTableAsync<TTable>(string tableCollectionName, Locale locale)
            where TTable : LocalizationTable
        {
            if (locale != null && locale.Identifier.Code == Plugin.Code && typeof(TTable) == typeof(AssetTable))
            {
                var enHandle = LocalizationSettings.AssetDatabase.GetTableAsync(tableCollectionName, Plugin.English);
                return Addressables.ResourceManager.CreateChainOperation<TTable, AssetTable>(enHandle, h =>
                {
                    if (h.Status != AsyncOperationStatus.Succeeded || h.Result == null)
                        return Addressables.ResourceManager.CreateCompletedOperation<TTable>(null,
                            $"Table d'assets anglaise {tableCollectionName} introuvable");
                    return Addressables.ResourceManager.CreateCompletedOperation(
                        Plugin.BuildFrenchAssets(h.Result, locale) as TTable, null);
                });
            }
            return previous != null ? previous.ProvideTableAsync<TTable>(tableCollectionName, locale) : default;
        }
    }
}
