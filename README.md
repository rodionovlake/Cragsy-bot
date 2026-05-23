# 🧗 Cragsy Bot

**Telegram bot that connects rock climbers for training together.**  
Think of it as Tinder, but for finding a climbing partner — swipe through profiles, match by city, level and style, chat directly inside Telegram.

> Built as a solo project. Reached real users, processed real payments, handled multilingual UX across 5 languages.

---

## What it does

- **Profile system** — name, photo, city (Geoapify autocomplete), climbing level (3A–9C), type (bouldering / lead), weight category, bio
- **Smart search** — filter by difficulty, type, gender, weight, city; preloads up to 500 profiles with background pagination
- **Likes & matching** — like / skip / hide mechanics, mutual match detection, "Who liked me" with premium unlock
- **In-bot messaging** — 1-on-1 chats between matched users with unread counter, mute, archive, delete
- **Bulletin board** — post climbing sessions with date, time, location; auto-expiration
- **Gym meetups** — pick a gym (Moscow / St. Petersburg), join a training session, group chat with all participants, auto-rewards after session
- **Push notifications** — delayed like notifications (60s debounce), photo reminders (3-touch system with 45-day reset), daily meetup pushes at 17:00 local time
- **Premium (Cragsy Boost)** — paid via Telegram Stars; enhanced visibility, advanced filters, founder badge
- **Content moderation** — report system (abuse / spam / inappropriate photo), admin panel with ban/unblock, user search, broadcast tools
- **4 languages** — English, Spanish, German, Russian — all UI texts, buttons, notifications

## Tech stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.11, asyncio |
| Telegram | python-telegram-bot 20.3 |
| Database | PostgreSQL (asyncpg pool + psycopg2 for migrations) |
| Geocoding | Geoapify Autocomplete API |
| Payments | Telegram Stars (native in-bot payments) |
| Hosting | Render (web service + managed PostgreSQL) |

## Architecture highlights

- **Async-first** — all handlers are `async`, DB access through `asyncpg` connection pool, background tasks via `asyncio.create_task()`
- **Auto-migrations** — schema updates run automatically on startup (`run_migrations()`), no manual SQL needed
- **Scalable search** — aggressive preloading of all matching profiles (up to 500), filter-change detection triggers automatic re-search
- **Delayed notifications** — like pushes use 60-second timer with deduplication to batch multiple likes into one notification
- **Safe message pattern** — unified handler pattern supports both direct messages and callback queries: `message = query.message if query else update.message`
- **Geopolitical handling** — correct country attribution for disputed territories (Crimea, Donetsk, Luhansk regions)

## Project structure

```
main.py                 — bot logic, handlers, DB, cron tasks (~17,500 lines)
TEXTS.py                — UI texts for all 4 languages (menus, messages, prompts)
TEXT2.py                — extended texts (admin, moderation, payments, meetups)
inline_texts.py         — button labels for all 4 languages
user_agreement_text.py  — user agreement / privacy policy
requirements.txt        — Python dependencies
.env.example            — required environment variables
```

## Setup

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in:
   - `BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
   - `DATABASE_URL` — PostgreSQL connection string
   - `GEOAPIFY_API_KEY` — from [geoapify.com](https://www.geoapify.com/)
   - `ADMIN_IDS` — comma-separated Telegram user IDs
   - `ADMIN_PASSWORD` — password for admin panel access
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run:
   ```bash
   python main.py
   ```

The bot will automatically create all required database tables and run migrations on first start.

## Screenshots

<!-- Add screenshots of the bot in action here -->
<!-- Example: ![Search](screenshots/search.png) -->

## Status

The project was actively developed and used by real climbers. Currently not running in production, published as a portfolio piece demonstrating:

- Full-cycle product development (idea → UX → code → launch → real users)
- Complex Telegram Bot API usage (payments, inline keyboards, media handling, callback routing)
- Async Python architecture with PostgreSQL
- Multilingual UX design
- Content moderation and admin tooling

## License

MIT
