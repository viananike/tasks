# 📝 Tasks — A Simple & Powerful Task Tracker

<div align="center">
  <img src="Logo/horizontal.png" alt="App Logo" width="600"/>
</div>

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

Follow these steps to run the app locally or on a remote machine using Docker:

1. **Clone the repository**  
   ```bash
   git clone https://github.com/viananike/tasks.git
   cd tasks
   ```
2. **Create a .env file**
   
   Copy the example file and fill in your own configuration values:
   
   ```bash
   cp .env.example .env
   ```
   Run the following command to add a secret key to your .env:
   ```bash
   echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
   ```
   ⚠️ **Security Tip**
   It is *strongly recommended* to change the default database credentials in your .env file. Make sure these values match what's defined under the db service in your docker-compose.yml
3. **Run with docker:**
   ```bash
   docker compose up -d
   ```
4. **Visit http://ip-of-your-machine:5000 and set up your admin account!**

---

## 🛣 Roadmap

Here's what might be coming soon (or eventually!):

- [ ] 🗓️ Calendar view
- [ ] 🌓 Light & Dark mode toggle
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
