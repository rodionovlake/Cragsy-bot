# texts.py

TEXTS = {
    "ru": {
        # Главное меню
        "menu_form": "📝 Профиль",
        "menu_search": "🧗 Поиск",
        "menu_likes": "❤️ Лайки",
        "menu_chats": "💬 Чаты",
        "menu_feedback": "✉️ Отзыв",
        "menu_about": "🐾 Еще",
        "menu_chalk": "🗯 Магнезия",
        "menu_home": "🏠 Меню",
        "btn_end_chat": "❌ Завершить чат",

        # Подменю "Поиск"
        "search_filters": "🧰 Фильтры",
        "search_find": "🔍 Найти",
        "search_hidden": "🙈 Скрытые",
        "search_back": "↩️ Назад",
        "search_next_person": "🔽",

        # Подменю "Лайки"
        "likes_sent": "❤️ Мои",
        "likes_received": "👀 Кто меня ❤️",
        "likes_mutual": "🤝 Взаимные ❤️",
        "likes_back": "↩️ Назад",

        # Подменю "Чаты"
        "chats_active": "🕒 Активные",
        "chats_requests": "🔔 Запросы",
        "chats_offline": "💤 Офлайн",
        "chats_back": "↩️ Назад",

        # Подменю "Магнезия"
        "chalk_get": "🤲 Получить",
        "chalk_use": "🗯 Использовать",
        "chalk_amount": "🎒 Количество",
        "chalk_status": "📊 Статус Boost",
        "chalk_back": "↩️ Назад",

        # Подменю "Получить магнезию"
        "chalk_get_referral": "👥 Пригласить друга",
        "chalk_get_board": "🤝 За объявления",
        "chalk_get_stars": "⭐ За Telegram Stars",
        "chalk_get_founder": "💎 Founder статус",
        "chalk_get_back": "↩️ В предыдущее меню",

        # Кнопки использования магнезии (Boost)
        "boost_buy_14_btn": "14 дней 🗯 Boost за 10 г",
        "boost_buy_182_btn": "182 дня 🗯 Boost за 110 г",
        "boost_buy_365_btn": "365 дней 🗯 Boost за 200 г",

        # Прогресс регистрации
        "reg_progress": "📋 Шаг {step} из 8",

        # Подменю "Анкета"
        "form_edit": "✏️ Редактировать",

        "form_delete": "🗑️ Удалить",
        "form_back": "↩️ Назад",

        # Подменю "Cragsy"
        "about_feedback": "✉️ Отзыв",
        "about_rules": "📄 Правила",
        "about_home": "🐾 Создать профиль заново",
        "about_back": "↩️ Назад",

        # Подменю "Офлайн"
        "offline_archive": "📦 Архив",
        "offline_muted": "🔇 Muted",
        "offline_back": "↩️ Назад в меню",

        # Подменю "Объявления
        "menu_board": "🤝 Встречи",
        "board_my": "📂 Мои",
        "board_create": "➕ Создать",
        "board_show_more_btn": "⬇️",
        "board_city": "🏠 Все залы",
        "board_back": "↩️ Назад",
        "board_menu_title": "🤝 Здесь появляются объявления для совместных тренировок",
        "board_create_intro": "📌 Давай создадим объявление.\n\nВыбери дату:",
        "board_date_today": "📅 Сегодня ({date})",
        "board_date_tomorrow": "📅 Завтра ({date})",
        "board_date_custom": "🗓 Другая дата",
        "board_time_intro": "🕒 Теперь выбери время начала:",
        "board_climb_type_intro": "🧱 Укажи тип лазания:",
        "board_weight_intro": "⚖️ Укажи свой вес:",
        "board_gym_intro": "🏟 Укажи зал, где планируешь встречу. Не более 50 символов:",
        "board_difficulty_intro": "📊 Укажи уровень лазания:",
        "board_gym_saved": "✅ Зал сохранён.",
        "board_gym_too_long": "❗️Слишком длинное название. Введи до 50 символов.",
        "board_preview_caption": "📌 Объявление:\n\n🗓 {date} в {time}\n🧗 {climb_type}\n⚖️ {weight}\n🏟 {gym}",
        "board_buttons_publish": "✅ Опубликовать",
        "board_buttons_remove": "❌ Снять",
        "board_buttons_edit": "✏️ Редактировать",
        "board_published": "✅ Объявление опубликовано.",
        "board_removed": "🔴 Объявление снято и в скором времени будет удалено.",
        "board_city_empty": "❌ Пока нет активных объявлений в твоём городе.",
        "board_city_loading": "🔍 Ищем объявления в твоём городе...",
        "board_profile_hidden": "🙈 Профиль скрыт.",
        "board_btn_profile": "👤",
        "board_btn_write": "✉️",
        "board_btn_status_active": "🟢",
        "board_btn_status_removed": "🔴",
        "board_profile_not_found": "❌ Профиль не найден.",
        "board_status_active_text": "🟢 Объявление активно ✅",
        "board_status_removed_text": "🔴 Объявление снято ❌",
        "board_custom_date_prompt": "📅 Введите дату вручную в формате: 25.06.2025",
        "board_custom_date_invalid": "❌ Неверный формат. Попробуйте ещё раз, например: 25.06.2025",
        "board_date_saved": "✅ Дата сохранена.",
        "board_empty": "📭 У тебя пока нет активных объявлений.",
        "status_active": "Активно",
        "status_removed": "Неактивно"

    },

    "en": {
        # Main menu
        "menu_form": "📝 Profile",
        "menu_search": "🧗 Search",
        "menu_likes": "❤️ Likes",
        "menu_chats": "💬 Chats",
        "menu_feedback": "✉️ Feedback",
        "menu_about": "🐾 More",
        "menu_chalk": "🗯 Chalk",
        "menu_home": "🏠 Menu",
        "btn_end_chat": "❌ End Chat",

        # Submenu "Search"
        "search_filters": "🧰 Filters",
        "search_find": "🔍 Find",
        "search_hidden": "🙈 Hidden",
        "search_back": "↩️ Back",
        "search_next_person": "🔽",

        # Submenu "Likes"
        "likes_sent": "❤️ My Likes",
        "likes_received": "👀 Liked Me ❤️",
        "likes_mutual": "🤝 Mutual ❤️",
        "likes_back": "↩️ Back",

        # Submenu "Chats"
        "chats_active": "🕒 Active",
        "chats_requests": "🔔 Requests",
        "chats_offline": "💤 Offline",
        "chats_back": "↩️ Back",

        # Submenu "Chalk"
        "chalk_get": "🤲 Get",
        "chalk_use": "🗯 Use",
        "chalk_amount": "🎒 Amount",
        "chalk_status": "📊 Boost Status",
        "chalk_back": "↩️ Back",

        # Submenu "Get Chalk"
        "chalk_get_referral": "👥 Invite a friend",
        "chalk_get_board": "🤝 For postings",
        "chalk_get_stars": "⭐ For Telegram Stars",
        "chalk_get_founder": "💎 Founder status",
        "chalk_get_back": "↩️ Back to previous menu",

        # Use Chalk buttons (Boost)
        "boost_buy_14_btn": "14 days 🗯 Boost for 10g",
        "boost_buy_182_btn": "182 days 🗯 Boost for 110g",
        "boost_buy_365_btn": "365 days 🗯 Boost for 200g",

        # Registration progress
        "reg_progress": "📋 Step {step} of 8",

        # Submenu "Form"
        "form_edit": "✏️ Change",
        "form_delete": "🗑️ Delete",
        "form_back": "↩️ Back",

        # Submenu "About"
        "about_feedback": "✉️ Feedback",
        "about_rules": "📄 Rules",
        "about_home": "🐾 Create profile again",
        "about_back": "↩️ Back",

        # Submenu "Offline"
        "offline_archive": "📦 Archive",
        "offline_muted": "🔇 Muted",
        "offline_back": "↩️ Back to menu",

        # Submenu "Board"
        "menu_board": "🤝 Meetups",
        "board_my": "📂 My Posts",
        "board_create": "➕ Create",
        "board_show_more_btn": "⬇️",
        "board_city": "🏠 All gyms",
        "board_back": "↩️ Back",
        "board_menu_title": "🤝 This is where posts for joint training sessions appear.\n🔔 After publishing a post, a notification will be sent to everyone in your city.\n🐾 Post regularly — and once a week I’ll sprinkle you some chalk to keep your sessions strong.",
        "board_create_intro": "📌 Let's create a new post.\n\nChoose a date:",
        "board_date_today": "📅 Today ({date})",
        "board_date_tomorrow": "📅 Tomorrow ({date})",
        "board_date_custom": "🗓 Other Date",
        "board_time_intro": "🕒 Now choose a start time:",
        "board_climb_type_intro": "🧱 Choose a climbing type:",
        "board_weight_intro": "⚖️ Enter your weight:",
        "board_gym_intro": "🏟 Specify the gym for the meeting (max 50 characters):",
        "board_difficulty_intro": "📊 Select your climbing level:",
        "board_gym_saved": "✅ Gym saved.",
        "board_gym_too_long": "❗️Name too long. Please enter up to 50 characters.",
        "board_preview_caption": "📌 Post:\n\n🗓 {date} at {time}\n🧗 {climb_type}\n⚖️ {weight}\n🏟 {gym}",
        "board_buttons_publish": "✅ Publish",
        "board_buttons_remove": "❌ Remove",
        "board_buttons_edit": "✏️ Edit",
        "board_published": "✅ Post published.",
        "board_removed": "🔴 Post removed and will be deleted soon.",
        "board_city_empty": "❌ No active posts in your city yet.",
        "board_city_loading": "🔍 Searching for posts in your city...",
        "board_profile_hidden": "🙈 Profile hidden.",
        "board_btn_profile": "👤",
        "board_btn_write": "✉️",
        "board_btn_status_active": "🟢",
        "board_btn_status_removed": "🔴",
        "board_profile_not_found": "❌ Profile not found.",
        "board_status_active_text": "🟢 Post is active ✅",
        "board_status_removed_text": "🔴 Post removed ❌",
        "board_custom_date_prompt": "📅 Enter the date manually in the format: 25.06.2025",
        "board_custom_date_invalid": "❌ Invalid format. Try again, e.g.: 25.06.2025",
        "board_date_saved": "✅ Date saved.",
        "board_empty": "📭 You have no active posts yet.",
        "status_active": "Active",
        "status_removed": "Inactive"

    },

    "es": {
        "menu_form": "📝 Perfil",
        "menu_search": "🧗 Buscar",
        "menu_likes": "❤️ Likes",
        "menu_chats": "💬 Chats",
        "menu_feedback": "✉️ Opinión",
        "menu_about": "🐾 Más",
        "menu_chalk": "🗯 Magnesio",
        "menu_home": "🏠 Menú",
        "btn_end_chat": "❌ Terminar chat",

        "search_filters": "🧰 Filtros",
        "search_find": "🔍 Buscar",
        "search_hidden": "🙈 Ocultos",
        "search_back": "↩️ Atrás",
        "search_next_person": "🔽",

        "likes_sent": "❤️ Mis likes",
        "likes_received": "👀 Me dieron like ❤️",
        "likes_mutual": "🤝 Mutuos ❤️",
        "likes_back": "↩️ Atrás",

        "chats_active": "🕒 Activos",
        "chats_requests": "🔔 Solicitudes",
        "chats_offline": "💤 Inactivos",
        "chats_back": "↩️ Atrás",

        "chalk_get": "🤲 Obtener",
        "chalk_use": "🗯 Usar",
        "chalk_amount": "🎒 Cantidad",
        "chalk_status": "📊 Estado Boost",
        "chalk_back": "↩️ Atrás",

        # Submenu "Obtener magnesio"
        "chalk_get_referral": "👥 Invitar a un amigo",
        "chalk_get_board": "🤝 Por anuncios",
        "chalk_get_stars": "⭐ Por Telegram Stars",
        "chalk_get_founder": "💎 Estado Founder",
        "chalk_get_back": "↩️ Volver al menú anterior",

        # Botones de uso de magnesio (Boost)
        "boost_buy_14_btn": "14 días 🗯 Boost por 10 g",
        "boost_buy_182_btn": "182 días 🗯 Boost por 110 g",
        "boost_buy_365_btn": "365 días 🗯 Boost por 200 g",

        # Progreso de registro
        "reg_progress": "📋 Paso {step} de 8",

        "form_edit": "✏️ Editar",
        "form_delete": "🗑️ Eliminar",
        "form_back": "↩️ Atrás",

        "about_feedback": "✉️ Opinión",
        "about_rules": "📄 Reglas",
        "about_home": "🐾 Crear el perfil de nuevo",
        "about_back": "↩️ Atrás",

        "offline_archive": "📦 Archivo",
        "offline_muted": "🔇 Silenciados",
        "offline_back": "↩️ Volver al menú",

        # Submenú "Anuncios"
        "menu_board": "🤝 Encuentros",
        "board_my": "📂 Mis Anuncios",
        "board_create": "➕ Crear",
        "board_show_more_btn": "⬇️",
        "board_city": "🏠 Salas",
        "board_back": "↩️ Atrás",
        "board_menu_title": "🤝 Aquí aparecen los anuncios para entrenamientos conjuntos.\n🔔 Después de publicar un anuncio, se envía una notificación a todos en tu ciudad.\n🐾 Publica anuncios — y una vez por semana te regalaré un poco de magnesio para una buena sesión.",
        "board_create_intro": "📌 Vamos a crear un anuncio.\n\nElige una fecha:",
        "board_date_today": "📅 Hoy ({date})",
        "board_date_tomorrow": "📅 Mañana ({date})",
        "board_date_custom": "🗓 Otra fecha",
        "board_time_intro": "🕒 Ahora elige la hora de inicio:",
        "board_climb_type_intro": "🧱 Indica el tipo de escalada:",
        "board_weight_intro": "⚖️ Indica tu peso:",
        "board_gym_intro": "🏟 Indica el gimnasio donde será la reunión (máx. 50 caracteres):",
        "board_difficulty_intro": "📊 Indica tu nivel de escalada:",
        "board_gym_saved": "✅ Gimnasio guardado.",
        "board_gym_too_long": "❗️Nombre demasiado largo. Máximo 50 caracteres.",
        "board_preview_caption": "📌 Anuncio:\n\n🗓 {date} a las {time}\n🧗 {climb_type}\n⚖️ {weight}\n🏟 {gym}",
        "board_buttons_publish": "✅ Publicar",
        "board_buttons_remove": "❌ Eliminar",
        "board_buttons_edit": "✏️ Editar",
        "board_published": "✅ Anuncio publicado.",
        "board_removed": "🔴 Anuncio eliminado y será borrado pronto.",
        "board_city_empty": "❌ Aún no hay anuncios activos en tu ciudad.",
        "board_city_loading": "🔍 Buscando anuncios en tu ciudad...",
        "board_profile_hidden": "🙈 Perfil oculto.",
        "board_btn_profile": "👤",
        "board_btn_write": "✉️",
        "board_btn_status_active": "🟢",
        "board_btn_status_removed": "🔴",
        "board_profile_not_found": "❌ Perfil no encontrado.",
        "board_status_active_text": "🟢 Anuncio activo ✅",
        "board_status_removed_text": "🔴 Anuncio eliminado ❌",
        "board_custom_date_prompt": "📅 Ingresa la fecha manualmente en el formato: 25.06.2025",
        "board_custom_date_invalid": "❌ Formato inválido. Intenta de nuevo, por ejemplo: 25.06.2025",
        "board_date_saved": "✅ Fecha guardada.",
        "board_empty": "📭 Aún no tienes anuncios activos.",
        "status_active": "Activo",
        "status_removed": "Inactivo"

    },

    "de": {
        "menu_form": "📝 Profil",
        "menu_search": "🧗 Suchen",
        "menu_likes": "❤️ Likes",
        "menu_chats": "💬 Chats",
        "menu_feedback": "✉️ Feedback",
        "menu_about": "🐾 Mehr",
        "menu_chalk": "🗯 Magnesia",
        "menu_home": "🏠 Menü",
        "btn_end_chat": "❌ Chat beenden",

        "search_filters": "🧰 Filter",
        "search_find": "🔍 Finden",
        "search_hidden": "🙈 Versteckte",
        "search_back": "↩️ Zurück",
        "search_next_person": "🔽",

        "likes_sent": "❤️ Meine Likes",
        "likes_received": "👀 Wer mich mag ❤️",
        "likes_mutual": "🤝 Gegenseitig ❤️",
        "likes_back": "↩️ Zurück",

        "chats_active": "🕒 Aktiv",
        "chats_requests": "🔔 Anfragen",
        "chats_offline": "💤 Offline",
        "chats_back": "↩️ Zurück",

        "chalk_get": "🤲 Holen",
        "chalk_use": "🗯 Verwenden",
        "chalk_amount": "🎒 Menge",
        "chalk_status": "📊 Boost Status",
        "chalk_back": "↩️ Zurück",

        # Submenu "Magnesia bekommen"
        "chalk_get_referral": "👥 Freund einladen",
        "chalk_get_board": "🤝 Für Anzeigen",
        "chalk_get_stars": "⭐ Für Telegram Stars",
        "chalk_get_founder": "💎 Founder-Status",
        "chalk_get_back": "↩️ Zurück zum vorherigen Menü",

        # Magnesia-Nutzungsschaltflächen (Boost)
        "boost_buy_14_btn": "14 Tage 🗯 Boost für 10 g",
        "boost_buy_182_btn": "182 Tage 🗯 Boost für 110 g",
        "boost_buy_365_btn": "365 Tage 🗯 Boost für 200 g",

        # Registrierungsfortschritt
        "reg_progress": "📋 Schritt {step} von 8",

        "form_edit": "✏️ Bearbeiten",
        "form_delete": "🗑️ Löschen",
        "form_back": "↩️ Zurück",

        "about_feedback": "✉️ Feedback",
        "about_rules": "📄 Regeln",
        "about_home": "🐾 Profil neu erstellen",
        "about_back": "↩️ Zurück",

        "offline_archive": "📦 Archiv",
        "offline_muted": "🔇 Stumm",
        "offline_back": "↩️ Zurück zum Menü",

        # Untermenü "Anzeigen"
        "menu_board": "🤝 Treffen",
        "board_my": "📂 Meine",
        "board_create": "➕ Erstellen",
        "board_show_more_btn": "⬇️",
        "board_city": "🏠 Hallen",
        "board_back": "↩️ Zurück",
        "board_menu_title": "🤝 Hier erscheinen Anzeigen für gemeinsame Trainingseinheiten.\n🔔 Nach dem Veröffentlichen wird eine Benachrichtigung an alle in deiner Stadt gesendet.\n🐾 Erstelle Anzeigen — und einmal pro Woche gebe ich dir etwas Chalk für eine starke Session.",
        "board_create_intro": "📌 Lass uns eine Anzeige erstellen.\n\nWähle ein Datum:",
        "board_date_today": "📅 Heute ({date})",
        "board_date_tomorrow": "📅 Morgen ({date})",
        "board_date_custom": "🗓 Anderes Datum",
        "board_time_intro": "🕒 Wähle nun eine Startzeit:",
        "board_climb_type_intro": "🧱 Gib den Klettertyp an:",
        "board_weight_intro": "⚖️ Gib dein Gewicht an:",
        "board_gym_intro": "🏟 Gib die Halle an (max. 50 Zeichen):",
        "board_difficulty_intro": "📊 Gib dein Kletterniveau an:",
        "board_gym_saved": "✅ Halle gespeichert.",
        "board_gym_too_long": "❗️Name zu lang. Maximal 50 Zeichen.",
        "board_preview_caption": "📌 Anzeige:\n\n🗓 {date} um {time}\n🧗 {climb_type}\n⚖️ {weight}\n🏟 {gym}",
        "board_buttons_publish": "✅ Veröffentlichen",
        "board_buttons_remove": "❌ Entfernen",
        "board_buttons_edit": "✏️ Bearbeiten",
        "board_published": "✅ Anzeige veröffentlicht.",
        "board_removed": "🔴 Anzeige entfernt und wird bald gelöscht.",
        "board_city_empty": "❌ Derzeit gibt es keine aktiven Anzeigen in deiner Stadt.",
        "board_city_loading": "🔍 Suche nach Anzeigen in deiner Stadt...",
        "board_profile_hidden": "🙈 Profil versteckt.",
        "board_btn_profile": "👤",
        "board_btn_write": "✉️",
        "board_btn_status_active": "🟢",
        "board_btn_status_removed": "🔴",
        "board_profile_not_found": "❌ Profil nicht gefunden.",
        "board_status_active_text": "🟢 Anzeige aktiv ✅",
        "board_status_removed_text": "🔴 Anzeige entfernt ❌",
        "board_custom_date_prompt": "📅 Gib das Datum manuell im Format ein: 25.06.2025",
        "board_custom_date_invalid": "❌ Ungültiges Format. Versuch es erneut, z. B.: 25.06.2025",
        "board_date_saved": "✅ Datum gespeichert.",
        "board_empty": "📭 Du hast noch keine aktiven Anzeigen.",
        "status_active": "Aktiv",
        "status_removed": "Inaktiv"

    },

    "fr": {
        "menu_form": "📝 Profil",
        "menu_search": "🧗 Recherche",
        "menu_likes": "❤️ J’aime",
        "menu_chats": "💬 Chats",
        "menu_feedback": "✉️ Avis",
        "menu_about": "🐾 À propos de Cragsy",
        "menu_chalk": "🗯 Magnésie",
        "menu_home": "🏠 Menu",
        "btn_end_chat": "❌ Fin du chat",

        "search_filters": "🧰 Filtres",
        "search_find": "🔍 Rechercher",
        "search_hidden": "🙈 Cachés",
        "search_back": "↩️ Retour",

        "likes_sent": "❤️ Mes likes",
        "likes_received": "👀 M’ont liké ❤️",
        "likes_mutual": "🤝 Réciproques ❤️",
        "likes_back": "↩️ Retour",

        "chats_active": "🕒 Actifs",
        "chats_requests": "🔔 Demandes",
        "chats_offline": "💤 Hors ligne",
        "chats_back": "↩️ Retour",

        "chalk_get": "🤲 Obtenir",
        "chalk_use": "🗯 Utiliser",
        "chalk_amount": "🎒 Quantité",
        "chalk_back": "↩️ Retour",

        "form_edit": "✏️ Modifier le profil",
        "form_delete": "🗑️ Supprimer le profil",
        "form_back": "↩️ Retour",

        "about_feedback": "✉️ Avis",
        "about_rules": "📄 Règles",
        "about_home": "🐾 Accueil",
        "about_back": "↩️ Retour",

        "offline_archive": "📦 Archive",
        "offline_muted": "🔇 Silencieux",
        "offline_back": "↩️ Retour"
    }
}
