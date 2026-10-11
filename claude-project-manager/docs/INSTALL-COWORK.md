---
description: Step-by-step installation guide for the Project Manager plugin for Claude Cowork — AI-powered IT project management automation.
---

# Installation Guide — Project Manager Plugin for Claude Cowork

[Русская версия](INSTALL-COWORK.ru.md)

This guide walks you through installing the Project Manager plugin in Claude Cowork and getting it ready for your first project. The process takes about 5 minutes.

---

## Requirements

Before you begin, make sure you have:

- **Claude desktop app** with Cowork mode enabled (macOS or Windows)
- **Claude Pro or Max subscription** — required for Cowork
- **A folder on your computer** where project files will be stored (you can create it during setup)
- **MCP integrations** (optional): Jira, Gmail, and Google Calendar accounts — only needed if you want the plugin to sync with those services automatically

> The plugin works fully without Jira, Gmail, or Calendar. Without them, it generates file-based documents with manual instructions instead of syncing automatically.

---

## Step 1 — Download the Plugin File

1. Open the GitHub repository: [project-manager-cowork-plugin](https://github.com/your-repo-link)
2. Click the **Releases** section on the right side of the page
3. Find the latest release (e.g. `v0.1.2`)
4. Under **Assets**, click `project-manager-X.X.X.plugin` to download it
5. Save the file to a convenient location (e.g. your Downloads folder)

The plugin is a single `.plugin` file — no unzipping or installation wizard required.

---

## Step 2 — Install the Plugin in Claude Cowork

1. Open the **Claude** desktop app on your computer
2. Switch to **Cowork** mode (button in the top-center navigation bar)
3. In the Cowork interface, click the **+** icon
4. Select **Plugins** from the menu
5. Click **Add Plugin**
6. Select **Install from file** and navigate to the `.plugin` file you downloaded in Step 1
7. Cowork will validate the plugin (this takes a few seconds)
8. Click **Install** to confirm

After installation, **Project Manager** will appear in your Plugins list.

> **If you see a "Plugin validation failed" error:** re-download the `.plugin` file from GitHub. The file may not have downloaded completely.

---

## Step 3 — Connect a Working Folder

The plugin creates and manages project files directly on your computer. You need to point it to a folder where projects will be stored.

1. In the Cowork interface, click **Work in a folder** (button in the bottom-left corner)
2. Choose an existing folder or create a new one (recommended: `~/Documents/projects/`)
3. Click **Allow** to grant Cowork access to the folder

> **Tip:** Use one shared folder for all your projects — the plugin will create a separate subfolder for each project inside it. For example: `~/Documents/projects/website-relaunch/`, `~/Documents/projects/mobile-app/`.

---

## Step 4 — Connect MCP Integrations (Optional)

MCP integrations let the plugin read and write data in Jira, Gmail, and Google Calendar automatically. This step is optional — skip it if you prefer to work with files only.

**To connect an integration:**

1. In the Cowork sidebar, click **Connectors**
2. Find the service you want to connect: **Atlassian (Jira)**, **Gmail**, or **Google Calendar**
3. Click **Connect**
4. You will be redirected to the service's login page (this is standard OAuth authorization — no passwords are shared with the plugin)
5. Log in and grant the requested permissions
6. Once authorized, the connector status will show **Connected**

Repeat for each service you want to use.

> You can connect or disconnect integrations at any time — it will not affect your project files or require reinstalling the plugin.

---

## Step 5 — Run Your First Command

Open a new Cowork session and type:

```
/init-project my-first-project
```

Replace `my-first-project` with a short name for your project (use hyphens instead of spaces, Latin characters recommended, e.g. `website-relaunch` or `mobile-app-v2`).

The plugin will:
- Create a folder structure for your project inside the working directory
- Generate a `CLAUDE.md` file with agent instructions
- Create a `project-state.md` file to track artifact status
- Begin Phase 1 (Project Initiation) and ask you for the first inputs

---

## Step 6 — Verify the Installation

If `/init-project` responds with a confirmation message that lists created folders and asks for project details — the installation is complete and working correctly.

To check the plugin status at any time:

```
/status
```

This will show the current project phase, completed artifacts, and next recommended steps.

---

## Troubleshooting

**Plugin does not appear in the list after installation**
→ Restart the Claude desktop app and try again.

**"Plugin validation failed" during installation**
→ Re-download the `.plugin` file from GitHub. The file may be incomplete.

**`/init-project` does not respond or shows an error**
→ Make sure you connected a working folder in Step 3 (click **Work in a folder** in the bottom-left corner). The plugin cannot create files without a folder connected.

**MCP connector shows "Authentication failed"**
→ Disconnect the integration and reconnect it. Make sure you are logged into the correct account in your browser during the authorization step.

**Files appear in the wrong location**
→ Click **Work in a folder** again and reselect the correct folder.

**Plugin was updated — do I need to reinstall?**
→ Yes. Click the **+** icon → **Plugins**, find Project Manager, remove it, then install the new `.plugin` file following Step 2.

---

[User Guide →](USER-GUIDE.md) | [Русская версия](INSTALL-COWORK.ru.md)
