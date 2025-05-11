# 📝 Tasks — A Simple & Powerful Task Tracker

Welcome to **Tasks**, a lightweight but powerful self-hostable task tracker built with Flask & Docker.  
Whether you're just trying to stay on top of your projects or you want to monitor a team's progress, **Tasks** has you covered.

---

## 🚀 Features

- 🔍 **Advanced Filtering** – Quickly filter tasks by user, date, or keyword.
- 📊 **Aggregate View** – View monthly totals of time spent per user.
- 👑 **Admin Panel** – Admins get access to:
  - 🧠 User statistics
  - 📜 Recent logs
  - 🛠 Project management
  - 👥 Admin account creation

---

## 📦 Getting Started

1. Create a docker-compose.yml
   ```yaml

   services:
   web:
      image: ghcr.io/viananike/tasks:latest
      ports:
         - "5000:5000"
      env_file:
         - .env
      depends_on:
         - db

   db:
      image: postgres:13
      environment:
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: postgres
         POSTGRES_DB: mytestdb
      volumes:
         - postgres_data:/var/lib/postgresql/data
         - ./db/init:/docker-entrypoint-initdb.d
      ports:
         - "5432:5432"

   volumes:
   postgres_data:
   ```
2. Create a .env file and fill it in with the variables necessary (Look at the .env.example in this repository)
3. Run with docker:
   ```bash
   docker compose up -d
4. Visit http://ip-of-your-machine:5000 and set up your admin account!

---

## 🛣 Roadmap

Here's what might be coming soon (or eventually!):

- [ ] 🗓️ Calendar view
- [ ] 📬 Email verification
- [ ] 🔔 Notification system
- [ ] 📎 File attachments
- [ ] 📱 Mobile-friendly tweaks

> Got an idea? [Open an issue](https://github.com/viananike/tasks/issues) or fork the project and go wild!

---

## 👨‍💻 About the Author

Hi! I'm just a hobbyist who loves:
- 🏡 Homelabbing  
- 🐳 Docker deployments  
- 👨‍💻 Building my own tools  

This project is maintained in my spare time. That means:
- 🐞 There **will** be bugs.  
- 🧪 Features may change or break.  
- 🛠️ Contributions and feedback are welcome!

---

## ⚠️ Disclaimer

Use at your own risk. Not intended for enterprise or mission-critical use... yet 😅

---

## 🧾 License

[MIT](LICENSE)

---

Thanks for checking out **Tasks**! ✨  
Made with ☕ and a love for tinkering.
