# zarya 🌅

**zarya** is a Telegram Mini App community event management platform designed to help small friend groups organize, discover, and register for social gatherings.

![zarya Preview](docs/assets/zarya_preview.png)

## 🎯 Overview

Small friend groups often lack a centralized, low-friction way to organize recurring social events. Current solutions like WhatsApp groups or shared notes create friction, scattered information, and poor event discoverability. 

zarya solves this by providing a single, always-accessible interface inside Telegram with a streamlined UX that minimizes the path to registration. Events are discovered immediately upon opening the app, and registration requires just two taps.

## ✨ Features (MVP)

- **Telegram Mini App:** Native-like experience inside Telegram.
- **Visual Event Discovery:** Browse all upcoming events with cover images.
- **Frictionless Registration:** 2-tap registration process.
- **Calendar Integration:** Export registered events to `.ics` format.
- **Admin Panel:** Manage events, registrations, and cover images via Telegram commands.
- **Russian Interface:** Fully localized for Russian-speaking users.

## 🏗️ Architecture

The application follows a modern, scalable architecture:

- **Frontend:** React + TypeScript (Telegram Web App)
- **Backend:** FastAPI (Python 3.11) + aiogram
- **Database:** PostgreSQL
- **Deployment:** Railway.com (Docker)

```text
Telegram Mini App (React) <--> FastAPI Backend <--> PostgreSQL
```

## 📂 Project Structure

```text
zarya/
├── frontend/           # React Mini App
├── backend/            # FastAPI & Telegram Bot
├── docs/               # PRD, UX analysis, and design assets
│   ├── prd.md
│   └── assets/
└── docker-compose.yml  # Local development setup
```

## 🚀 Getting Started

*Instructions for local development will be added as implementation progresses.*

## 📄 Documentation

- [Product Requirements Document (PRD)](docs/prd.md)
- [UX/UI Analysis](docs/ux_ui_analysis.md)

## 🤝 Contributing

This project is currently in the MVP phase and managed by the core team.

---
*Built with ❤️ for the zarya community.*
