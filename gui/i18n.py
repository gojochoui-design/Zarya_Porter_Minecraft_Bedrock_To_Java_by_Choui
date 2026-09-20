LANGS = [
    ("en", "English"),
    ("es", "Español"),
    ("ru", "Русский"),
    ("ja", "日本語"),
]

DEFAULT_LANG = "en"

_current = DEFAULT_LANG

STR = {
    "brand_sub": {
        "en": "J A V A   TO   B E D R O C K   C O N V E R T E R",
        "es": "C O N V E R T I D O R   D E   J A V A   A   B E D R O C K",
        "ru": "К О Н В Е Р Т Е Р   I Z   J A V A   V   B E D R O C K",
        "ja": "J A V A  か ら  B E D R O C K  へ 変 換",
    },
    "full_screen": {
        "en": "Full screen", "es": "Pantalla completa",
        "ru": "Во весь экран", "ja": "全画面",
    },
    "settings": {
        "en": "Settings", "es": "Ajustes", "ru": "Настройки", "ja": "設定",
    },
    "footer_by": {
        "en": "by choui - not affiliated with Mojang",
        "es": "por choui - no afiliado a Mojang",
        "ru": "от choui - не связан с Mojang",
        "ja": "by choui - Mojangとは無関係",
    },
    "reset_options": {
        "en": "Reset options", "es": "Restaurar opciones",
        "ru": "Сбросить опции", "ja": "オプションをリセット",
    },
    "drop_hint": {
        "en": "Drop your Java pack here, or pick it with the buttons",
        "es": "Suelta tu pack de Java aquí o elígelo con los botones",
        "ru": "Перетащите Java-пакет сюда или выберите кнопками",
        "ja": "Javaパックをここにドロップ、またはボタンで選択",
    },
    "chip_no_pack": {
        "en": "no pack", "es": "sin pack", "ru": "нет пакета", "ja": "パックなし",
    },
    "sky_title": {
        "en": "S K Y B O X E S", "es": "C I E L O S",
        "ru": "Н Е Б Е С А", "ja": "ス カ イ ボ ッ ク ス",
    },
    "sky_summary": {
        "en": "%d world(s) · %d sky(s) · %d environment",
        "es": "%d mundo(s) · %d cielo(s) · %d entorno",
        "ru": "%d мир(ов) · %d небо(сел) · %d окружения",
        "ja": "ワールド %d · 空 %d · 環境 %d",
    },
    "sky_layers": {
        "en": "%d layer(s)", "es": "%d capa(s)",
        "ru": "Слоёв: %d", "ja": "レイヤー %d",
    },
    "sky_fades": {
        "en": "fade %s", "es": "fundido %s",
        "ru": "затухание %s", "ja": "フェード %s",
    },
    "sky_rotate": {
        "en": "rotating", "es": "rota",
        "ru": "вращается", "ja": "回転する",
    },
    "sky_static": {
        "en": "static", "es": "estático",
        "ru": "статично", "ja": "固定",
    },
    "sky_pick_hint": {
        "en": "click a sky to use it in Bedrock",
        "es": "haz clic en un cielo para usarlo en Bedrock",
        "ru": "нажмите на небо, чтобы использовать его в Bedrock",
        "ja": "空をクリックしてBedrockで使用",
    },
    "sky_auto_chip": {
        "en": "SKY: AUTO", "es": "CIELO: AUTO",
        "ru": "НЕБО: АВТО", "ja": "空: 自動",
    },
    "sky_using_chip": {
        "en": "SKY: %s", "es": "CIELO: %s",
        "ru": "НЕБО: %s", "ja": "空: %s",
    },
    "sky_clear": {
        "en": "auto", "es": "auto", "ru": "авто", "ja": "自動",
    },
    "sky_pick_tip": {
        "en": "Click to use this sky in the converted pack",
        "es": "Haz clic para usar este cielo en el pack convertido",
        "ru": "Нажмите, чтобы использовать это небо в конвертированном пакете",
        "ja": "クリックでこの空を変換パックで使用",
    },
    "sky_missing_tip": {
        "en": "Texture missing from the pack - cannot be used",
        "es": "Falta la textura en el pack - no se puede usar",
        "ru": "Текстуры нет в пакете - нельзя использовать",
        "ja": "パックにテクスチャがない - 使用できません",
    },
    "sky_props": {
        "en": "props: %s", "es": "props: %s",
        "ru": "свойства: %s", "ja": "設定: %s",
    },
    "sky_env_note": {
        "en": "Ported to Bedrock by the Environment option",
        "es": "Se convierte a Bedrock con la opción Environment",
        "ru": "Переносится в Bedrock опцией Environment",
        "ja": "EnvironmentオプションでBedrockへ変換",
    },
    "sky_env": {
        "en": "Environment", "es": "Entorno",
        "ru": "Окружение", "ja": "環境",
    },
    "sky_phase_dawn": {
        "en": "Dawn", "es": "Amanecer",
        "ru": "Рассвет", "ja": "夜明け",
    },
    "sky_phase_day": {
        "en": "Day", "es": "Día",
        "ru": "День", "ja": "昼",
    },
    "sky_phase_dusk": {
        "en": "Dusk", "es": "Atardecer",
        "ru": "Закат", "ja": "夕方",
    },
    "sky_phase_night": {
        "en": "Night", "es": "Noche",
        "ru": "Ночь", "ja": "夜",
    },
    "sky_phase_all": {
        "en": "All day", "es": "Todo el día",
        "ru": "Весь день", "ja": "終日",
    },
    "sky_missing_img": {
        "en": "no image", "es": "sin imagen",
        "ru": "нет картинки", "ja": "画像なし",
    },
    "sky_missing_note": {
        "en": "declared as %s but the texture is not in the pack",
        "es": "declarado como %s pero la textura no está en el pack",
        "ru": "заявлен как %s, но текстуры нет в пакете",
        "ja": "%sと宣言されているがパックに画像がない",
    },
    "sky_always": {
        "en": "always visible", "es": "siempre visible",
        "ru": "всегда виден", "ja": "常に表示",
    },
    "no_version_read": {
        "en": "version could not be read", "es": "no se pudo leer la versión",
        "ru": "не удалось определить версию", "ja": "バージョンを読み取れませんでした",
    },
    "supported_hint": {
        "en": "Supported: .zip, .mcpack, a folder with pack.mcmeta - nested packs are found automatically",
        "es": "Compatible: .zip, .mcpack, una carpeta con pack.mcmeta - los packs anidados se detectan solos",
        "ru": "Поддерживается: .zip, .mcpack, папка с pack.mcmeta - вложенные пакеты находятся автоматически",
        "ja": "対応: .zip、.mcpack、pack.mcmeta入りのフォルダ - ネストしたパックも自動検出",
    },
    "hint_change": {
        "en": "Click a button to change it - version is read from pack.mcmeta and the pack contents",
        "es": "Pulsa un botón para cambiarlo - la versión se lee del pack.mcmeta y del contenido",
        "ru": "Нажмите кнопку, чтобы изменить - версия читается из pack.mcmeta и содержимого",
        "ja": "ボタンで変更 - バージョンはpack.mcmetaと中身から判定",
    },
    "choose_file": {
        "en": "Choose file...", "es": "Elegir archivo...",
        "ru": "Выбрать файл...", "ja": "ファイルを選択...",
    },
    "choose_folder": {
        "en": "Choose folder...", "es": "Elegir carpeta...",
        "ru": "Выбрать папку...", "ja": "フォルダを選択...",
    },
    "pick_pack_dialog": {
        "en": "Choose a Java resource pack", "es": "Elige un pack de recursos de Java",
        "ru": "Выберите Java-пакет ресурсов", "ja": "Javaリソースパックを選択",
    },
    "pick_dir_dialog": {
        "en": "Choose the pack folder", "es": "Elige la carpeta del pack",
        "ru": "Выберите папку пакета", "ja": "パックのフォルダを選択",
    },
    "save_as": {
        "en": "SAVE AS", "es": "GUARDAR COMO", "ru": "СОХРАНИТЬ КАК", "ja": "保存形式",
    },
    "path_placeholder": {
        "en": "Choose where to save the converted pack...",
        "es": "Elige dónde guardar el pack convertido...",
        "ru": "Выберите, куда сохранить сконвертированный пакет...",
        "ja": "変換したパックの保存先を選択...",
    },
    "convert": {
        "en": "CONVERT", "es": "CONVERTIR", "ru": "КОНВЕРТИРОВАТЬ", "ja": "変換",
    },
    "converting": {
        "en": "CONVERTING...", "es": "CONVIRTIENDO...",
        "ru": "КОНВЕРТАЦИЯ...", "ja": "変換中...",
    },
    "open_folder": {
        "en": "OPEN FOLDER", "es": "ABRIR CARPETA",
        "ru": "ОТКРЫТЬ ПАПКУ", "ja": "フォルダを開く",
    },
    "status_ready": {
        "en": "Ready - pick a pack to start", "es": "Listo - elige un pack para empezar",
        "ru": "Готово - выберите пакет", "ja": "準備完了 - パックを選択してください",
    },
    "status_done": {
        "en": "Done - saved where you chose", "es": "Hecho - guardado donde elegiste",
        "ru": "Готово - сохранено в выбранное место", "ja": "完了 - 選択した場所に保存しました",
    },
    "status_failed": {
        "en": "Failed - see the log below", "es": "Falló - mira el registro abajo",
        "ru": "Ошибка - смотрите журнал ниже", "ja": "失敗 - 下のログを確認",
    },
    "msg_pick_pack": {
        "en": "Pick a Java resource pack first.",
        "es": "Primero elige un pack de recursos de Java.",
        "ru": "Сначала выберите Java-пакет ресурсов.",
        "ja": "まずJavaリソースパックを選んでください。",
    },
    "msg_wait_convert": {
        "en": "Wait for the conversion to finish before changing the language.",
        "es": "Espera a que termine la conversión antes de cambiar el idioma.",
        "ru": "Дождитесь окончания конвертации, прежде чем менять язык.",
        "ja": "言語を変更する前に変換が終わるのをお待ちください。",
    },
    "save_dialog_title": {
        "en": "Save converted pack as", "es": "Guardar pack convertido como",
        "ru": "Сохранить сконвертированный пакет как", "ja": "変換したパックに名前を付けて保存",
    },
    "log_selected": {
        "en": "Selected pack: %s", "es": "Pack seleccionado: %s",
        "ru": "Выбран пакет: %s", "ja": "選択したパック: %s",
    },
    "log_detected": {
        "en": "Detected Java version: %s", "es": "Versión Java detectada: %s",
        "ru": "Определена версия Java: %s", "ja": "検出したJavaバージョン: %s",
    },
    "log_detection": {
        "en": "Detection: %s", "es": "Detección: %s",
        "ru": "Определение: %s", "ja": "判定: %s",
    },
    "log_starting": {
        "en": "Starting conversion...", "es": "Empezando conversión...",
        "ru": "Начинаю конвертацию...", "ja": "変換を開始...",
    },
    "log_sky_selected": {
        "en": "Sky chosen by you: %s",
        "es": "Cielo elegido por ti: %s",
        "ru": "Небо выбрано вами: %s",
        "ja": "選択した空: %s",
    },
    "log_sky_auto": {
        "en": "Sky: auto (the converter picks the best one - click a sky card to choose yours)",
        "es": "Cielo: auto (el conversor elige el mejor - haz clic en una tarjeta para elegir el tuyo)",
        "ru": "Небо: авто (конвертер выбирает лучшее - нажмите на карточку, чтобы выбрать своё)",
        "ja": "空: 自動（変換器が最適なものを選択 - カードをクリックして選べます）",
    },
    "log_all_set": {
        "en": "All set! Import the file into Minecraft Bedrock and activate it.",
        "es": "¡Listo! Importa el archivo en Minecraft Bedrock y actívalo.",
        "ru": "Всё готово! Импортируйте файл в Minecraft Bedrock и включите его.",
        "ja": "完了！ファイルをMinecraft Bedrockにインポートして有効化してください。",
    },
    "log_failed": {
        "en": "Conversion failed: %s", "es": "La conversión falló: %s",
        "ru": "Ошибка конвертации: %s", "ja": "変換に失敗しました: %s",
    },
    "log_reset": {
        "en": "Options reset to defaults", "es": "Opciones restauradas a los valores iniciales",
        "ru": "Опции сброшены по умолчанию", "ja": "オプションを初期値に戻しました",
    },
    "set_theme": {
        "en": "Color theme", "es": "Tema de color",
        "ru": "Цветовая тема", "ja": "カラーテーマ",
    },
    "set_language": {
        "en": "Language", "es": "Idioma", "ru": "Язык", "ja": "言語",
    },
    "set_save_folder": {
        "en": "Default save folder", "es": "Carpeta de guardado por defecto",
        "ru": "Папка сохранения по умолчанию", "ja": "既定の保存フォルダ",
    },
    "set_savefolder_hint": {
        "en": "Converted packs are saved here by default - leave empty to save next to the source pack",
        "es": "Los packs convertidos se guardan aquí por defecto - déjalo vacío para guardar junto al pack original",
        "ru": "Сконвертированные пакеты сохраняются здесь по умолчанию - оставьте пустым, чтобы сохранять рядом с исходным пакетом",
        "ja": "変換したパックの既定の保存先 - 空欄なら元パックの隣に保存します",
    },
    "set_clear": {
        "en": "Clear", "es": "Limpiar", "ru": "Очистить", "ja": "クリア",
    },
    "set_close": {
        "en": "Close", "es": "Cerrar", "ru": "Закрыть", "ja": "閉じる",
    },
    "scan_packs": {
        "en": "Scan for packs", "es": "Buscar packs",
        "ru": "Найти пакеты", "ja": "パックを検索",
    },
    "theme_btn": {
        "en": "Theme: %s", "es": "Tema: %s", "ru": "Тема: %s", "ja": "テーマ: %s",
    },
    "lang_btn": {
        "en": "Lang: %s", "es": "Idioma: %s", "ru": "Язык: %s", "ja": "言語: %s",
    },
    "set_hint": {
        "en": "Changes apply instantly and are remembered",
        "es": "Los cambios se aplican al instante y se recuerdan",
        "ru": "Изменения применяются сразу и запоминаются",
        "ja": "変更はすぐに反映され、記憶されます",
    },
    "sec_textures": {
        "en": "TEXTURES", "es": "TEXTURAS", "ru": "ТЕКСТУРЫ", "ja": "テクスチャ",
    },
    "sec_world": {
        "en": "WORLD AND MEDIA", "es": "MUNDO Y MULTIMEDIA",
        "ru": "МИР И МЕДИА", "ja": "ワールドとメディア",
    },
    "sec_hud": {
        "en": "HUD AND MENUS", "es": "HUD Y MENÚS", "ru": "HUD И МЕНЮ", "ja": "HUDとメニュー",
    },
    "opt_blocks_t": {
        "en": "Blocks & items", "es": "Bloques e items",
        "ru": "Блоки и предметы", "ja": "ブロックとアイテム",
    },
    "opt_blocks_d": {
        "en": "Every block and item texture your pack has, renamed to the Bedrock names",
        "es": "Todas las texturas de bloques e items de tu pack, renombradas a los nombres de Bedrock",
        "ru": "Все текстуры блоков и предметов вашего пакета, переименованные под имена Bedrock",
        "ja": "パック内のすべてのブロック・アイテムのテクスチャをBedrockの名前に変更",
    },
    "opt_entities_t": {
        "en": "Entity skins", "es": "Skins de entidades",
        "ru": "Скины существ", "ja": "エンティティのスキン",
    },
    "opt_entities_d": {
        "en": "Mob, player and armor layer textures, copied with their Bedrock layout",
        "es": "Texturas de mobs, jugadores y capas de armadura, copiadas con su disposición de Bedrock",
        "ru": "Текстуры мобов, игроков и слоёв брони, скопированные в раскладке Bedrock",
        "ja": "Mob・プレイヤー・防具レイヤーのテクスチャをBedrock配置でコピー",
    },
    "opt_flipbook_t": {
        "en": "Animated textures", "es": "Texturas animadas",
        "ru": "Анимированные текстуры", "ja": "アニメーションテクスチャ",
    },
    "opt_flipbook_d": {
        "en": "Your pack's water, lava, fire and portal animations keep their own timing",
        "es": "Las animaciones de agua, lava, fuego y portal de tu pack mantienen su propio ritmo",
        "ru": "Анимации воды, лавы, огня и портала из вашего пакета сохраняют свой темп",
        "ja": "パックの水・溶岩・火・ポータルのアニメが独自の速度を維持",
    },
    "opt_lowercase_t": {
        "en": "Lowercase filenames", "es": "Nombres en minúsculas",
        "ru": "Имена файлов в нижнем регистре", "ja": "小文字のファイル名",
    },
    "opt_lowercase_d": {
        "en": "Bedrock only finds lowercase paths - this renames everything safely",
        "es": "Bedrock solo encuentra rutas en minúsculas - esto renombra todo de forma segura",
        "ru": "Bedrock видит только пути в нижнем регистре - всё переименовывается безопасно",
        "ja": "Bedrockは小文字のパスのみ認識 - すべて安全にリネームします",
    },
    "opt_pack_icon_t": {
        "en": "Pack icon", "es": "Icono del pack",
        "ru": "Иконка пакета", "ja": "パックのアイコン",
    },
    "opt_pack_icon_d": {
        "en": "Show your pack's own pack.png as the icon inside Bedrock",
        "es": "Muestra el pack.png de tu pack como icono dentro de Bedrock",
        "ru": "Показывает pack.png вашего пакета как иконку в Bedrock",
        "ja": "パックのpack.pngをBedrock内のアイコンとして表示",
    },
    "opt_environment_t": {
        "en": "Sky, weather & moon", "es": "Cielo, clima y luna",
        "ru": "Небо, погода и луна", "ja": "空・天候・月",
    },
    "opt_environment_d": {
        "en": "Sun, moon phases, clouds and the powder snow freeze overlay",
        "es": "Sol, fases de la luna, nubes y la capa de congelación por nieve polvo",
        "ru": "Солнце, фазы луны, облака и оверлей заморозки от снега",
        "ja": "太陽・月相・雲・パウダースノーの凍結オーバーレイ",
    },
    "opt_panorama_t": {
        "en": "Panorama & title", "es": "Panorama y título",
        "ru": "Панорама и логотип", "ja": "パノラマとタイトル",
    },
    "opt_panorama_d": {
        "en": "The rotating menu background and the Minecraft title logo",
        "es": "El fondo giratorio del menú y el logo de Minecraft",
        "ru": "Вращающийся фон меню и логотип Minecraft",
        "ja": "メニューの回転背景とMinecraftのロゴ",
    },
    "opt_sounds_t": {
        "en": "Sounds", "es": "Sonidos", "ru": "Звуки", "ja": "サウンド",
    },
    "opt_sounds_d": {
        "en": "Every .ogg your pack ships, wired into Bedrock sound definitions",
        "es": "Todos los .ogg de tu pack, cableados en las definiciones de sonido de Bedrock",
        "ru": "Все .ogg вашего пакета, подключённые к определениям звуков Bedrock",
        "ja": "パック内の全.oggをBedrockのサウンド定義に接続",
    },
    "opt_fonts_t": {
        "en": "Fonts", "es": "Fuentes", "ru": "Шрифты", "ja": "フォント",
    },
    "opt_fonts_d": {
        "en": "Custom glyphs, accented letters and the ascii.png bitmap font",
        "es": "Glifos personalizados, letras acentuadas y la fuente bitmap ascii.png",
        "ru": "Свои глифы, буквы с акцентами и растровый шрифт ascii.png",
        "ja": "独自グリフ・アクセント文字・ascii.pngビットマップフォント",
    },
    "opt_hud_t": {
        "en": "HUD - crosshair, hearts, hotbar", "es": "HUD - mira, corazones, hotbar",
        "ru": "HUD - прицел, сердца, хотбар", "ja": "HUD - 十字線・ハート・ホットバー",
    },
    "opt_hud_d": {
        "en": "Slices icons.png and widgets.png into the exact pieces Bedrock asks for",
        "es": "Corta icons.png y widgets.png en las piezas exactas que Bedrock pide",
        "ru": "Режет icons.png и widgets.png точно на части, которые требует Bedrock",
        "ja": "icons.pngとwidgets.pngをBedrockが求める形に正確に分割",
    },
    "opt_chouiui_t": {
        "en": "Classic menus (ChouiUI 1.8)", "es": "Menús clásicos (ChouiUI 1.8)",
        "ru": "Классические меню (ChouiUI 1.8)", "ja": "クラシックメニュー(ChouiUI 1.8)",
    },
    "opt_chouiui_d": {
        "en": "Classic 1.8 containers everywhere; in creative the default block list stays "
              "plus a fold-away 1.8 panel (X button, and an H button that leaves only the inventory)",
        "es": "Contenedores clásicos 1.8 en todas partes; en creativo se queda la lista de bloques "
              "por defecto más un panel 1.8 plegable (botón X, y un botón H que deja solo el inventario)",
        "ru": "Классические контейнеры 1.8 везде; в креативе остаётся стандартный список блоков "
              "плюс складная панель 1.8 (кнопка X, и кнопка H, оставляющая только инвентарь)",
        "ja": "どこでもクラシックな1.8コンテナ；クリエイティブは標準ブロック一覧＋折りたたみ1.8パネル"
              "（Xボタン、Hボタンでインベントリのみ）",
    },
    "stage_Preparing...": {
        "en": "Preparing...", "es": "Preparando...", "ru": "Подготовка...", "ja": "準備中...",
    },
    "stage_Port textures": {
        "en": "Porting textures...", "es": "Portando texturas...",
        "ru": "Переношу текстуры...", "ja": "テクスチャを変換中...",
    },
    "stage_Converting animations...": {
        "en": "Converting animations...", "es": "Convirtiendo animaciones...",
        "ru": "Конвертирую анимации...", "ja": "アニメーションを変換中...",
    },
    "stage_Slicing HUD elements...": {
        "en": "Slicing HUD elements...", "es": "Cortando elementos del HUD...",
        "ru": "Нарезаю элементы HUD...", "ja": "HUD要素を分割中...",
    },
    "stage_Port sky...": {
        "en": "Porting sky...", "es": "Portando el cielo...",
        "ru": "Переношу небо...", "ja": "空を変換中...",
    },
    "stage_Port panorama...": {
        "en": "Porting panorama...", "es": "Portando el panorama...",
        "ru": "Переношу панораму...", "ja": "パノラマを変換中...",
    },
    "stage_Port sounds...": {
        "en": "Porting sounds...", "es": "Portando sonidos...",
        "ru": "Переношу звуки...", "ja": "サウンドを変換中...",
    },
    "stage_Port fonts...": {
        "en": "Porting fonts...", "es": "Portando fuentes...",
        "ru": "Переношу шрифты...", "ja": "フォントを変換中...",
    },
    "stage_Building classic menus (ChouiUI)...": {
        "en": "Building classic menus (ChouiUI)...",
        "es": "Construyendo menús clásicos (ChouiUI)...",
        "ru": "Собираю классические меню (ChouiUI)...",
        "ja": "クラシックメニューを作成中(ChouiUI)...",
    },
    "stage_Normalizing filenames...": {
        "en": "Normalizing filenames...", "es": "Normalizando nombres...",
        "ru": "Нормализую имена файлов...", "ja": "ファイル名を正規化中...",
    },
    "stage_Packaging...": {
        "en": "Packaging...", "es": "Empaquetando...",
        "ru": "Упаковка...", "ja": "パッケージ化中...",
    },
    "stage_Done": {
        "en": "Done", "es": "Hecho", "ru": "Готово", "ja": "完了",
    },
}

STAGE_KEYS = [
    "stage_Preparing...",
    "stage_Port textures",
    "stage_Converting animations...",
    "stage_Slicing HUD elements...",
    "stage_Port sky...",
    "stage_Port panorama...",
    "stage_Port sounds...",
    "stage_Port fonts...",
    "stage_Building classic menus (ChouiUI)...",
    "stage_Normalizing filenames...",
    "stage_Packaging...",
    "stage_Done",
]

STAGE_ENGINE = {
    "stage_Preparing...": "Preparing...",
    "stage_Port textures": "Porting textures...",
    "stage_Converting animations...": "Converting animations...",
    "stage_Slicing HUD elements...": "Slicing HUD elements...",
    "stage_Port sky...": "Porting sky...",
    "stage_Port panorama...": "Porting panorama...",
    "stage_Port sounds...": "Porting sounds...",
    "stage_Port fonts...": "Porting fonts...",
    "stage_Building classic menus (ChouiUI)...": "Building classic menus (ChouiUI)...",
    "stage_Normalizing filenames...": "Normalizing filenames...",
    "stage_Packaging...": "Packaging...",
    "stage_Done": "Done",
}


def set_language(code):
    global _current
    _current = code if code in dict(LANGS) else DEFAULT_LANG


def current_language():
    return _current


def lang_name(code):
    return dict(LANGS).get(code, code)


def tr(key, *args):
    entry = STR.get(key)
    if not entry:
        text = key
    else:
        text = entry.get(_current) or entry["en"]
    if args:
        try:
            text = text % args
        except TypeError:
            pass
    return text
