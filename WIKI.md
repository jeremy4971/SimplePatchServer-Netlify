# Simple Patch Server - Netlify Edition

The Simple Patch Server (SPS) is a serverless patch server for Jamf Pro administrators.

With the SPS you can host your own software title patch definitions for custom patch policies.

The patch server is a static site hosted on [Netlify's free plan](#deploy-on-netlify), with your patch definitions kept as JSON files in git.

## Contents

- Deploy and Setup
  - [Deploy on Netlify](#deploy-on-netlify)
  - [Setup in Jamf Pro](#setup-in-jamf-pro)
- Managing Your Patch Server
  - [Managing Patch Definitions](#managing-patch-definitions)
- API Documentation
  - [Patch Endpoints](#patch-endpoints)

## Deploy on Netlify

How to host the patch server as a static site on Netlify's free plan.

The Netlify deployment has no database and no write API. Your patch definitions are JSON files in a git repository. Each push to the repository rebuilds the site.

### Prerequisites

- A GitHub account (or GitLab / Bitbucket).
- A free Netlify account.

### Create the Repository

1. Push this project to a new repository in your GitHub account:

   ```bash
   git init
   git add .
   git commit -m "Initial patch server"
   git remote add origin git@github.com:<you>/<repo>.git
   git push -u origin main
   ```

2. Add your patch definitions to the `definitions/` folder (see [Managing Patch Definitions](#managing-patch-definitions)).

### Connect the Site in Netlify

1. In Netlify, choose **Add new site > Import an existing project** and select your repository.
2. Leave the build settings empty. They are read from `netlify.toml`:
   - Build command: `pip install -r requirements.txt && python scripts/build.py`
   - Publish directory: `public`
3. Deploy the site. Your patch server is now available at `https://<site-name>.netlify.app`.

Open `https://<site-name>.netlify.app/` in a browser to see the status page. It checks that `/software` responds correctly and shows the software titles being served and when the site was last built. The page source is `static/index.html`.

If a patch definition fails validation, the build fails and Netlify keeps serving the previous deploy.

> **Note:** Every push to the repository triggers a production deploy, which uses credits from your Netlify plan. On the free plan, each production deploy costs 15 of your 300 monthly credits, which allows about 20 deploys a month.

Next, [add the patch server to Jamf Pro](#setup-in-jamf-pro).

## Setup in Jamf Pro

How to configure the patch server as an External Patch Source in Jamf Pro.

> **Note:** "External Patch Sources" is a feature of Jamf Pro v10.2+.

To add your Patch Server as a `Patch External Source` in Jamf Pro, go to:

**Settings > Computer Management > Patch Management**

1. Click the `+ New` button next to `Patch External Source`.
2. Give the Patch Server a name.
3. Enter the URL without the schema (i.e. `https://`) in the `SERVER AND PORT` field (e.g. `<site-name>.netlify.app`) and 443 for the `PORT`.
4. Check the `Use SSL` box.

The Patch Server will now be available to subscribe to when adding new titles under `Patch Management`:

**Computers > Patch Management**

## Managing Patch Definitions

Manage your patch definition files for your patch server.

### Add a Patch Definition

To make a patch title available on your Patch Server, save the JSON file of the full patch definition into the `definitions/` folder of your repository, then commit and push.

> **Note:** **The JSON filename must match the software title ID of the patch.**

Examples taken from Jamf's official patch server would be saved as:

```text
definitions/AdobeAcrobatProDC.json
definitions/Composer.json
definitions/GoogleChrome.json
definitions/JavaSEDevelopmentKit8.json
definitions/macOS.json
definitions/MicrosoftWord2016.json
```

Every definition is validated against `schemas/schema_full_definition.json` during the build. If one is invalid, the build fails and the site keeps serving the previous deploy. To check your changes before pushing, run the build locally:

```bash
pip install -r requirements.txt
python scripts/build.py
```

### Update a Patch Definition

To replace a patch definition, overwrite its file in `definitions/`, then commit and push.

To add a single new version to an existing definition, save the version's JSON (the same format as a single item in the `patches` array) to a file and run:

```bash
python scripts/add_version.py <title-id> <version.json>
```

This validates the version against `schemas/schema_version.json`, rejects a version that already exists, inserts the new version at the top of `patches`, and updates `currentVersion` and `lastModified`. Commit and push the changed file to deploy it.

### Remove a Patch Definition

Delete its file from `definitions/`, then commit and push.

## Patch Endpoints

All about the patch endpoints that deliver the patch definitions to Jamf Pro.

The following endpoints are exposed for this service for your Jamf Pro server to view and subscribe to available patch titles:

- `/software` : Lists all available patch titles that are hosted on your Patch Server. They will be returned in the following JSON format:

  ```json
  [
      {
          "name": "string",
          "publisher": "string",
          "lastModified": "ISO date string",
          "currentVersion": "string",
          "id": "TitleName1"
      },
      {
          "name": "string",
          "publisher": "string",
          "lastModified": "ISO date string",
          "currentVersion": "string",
          "id": "TitleName2"
      },
      {
          "name": "string",
          "publisher": "string",
          "lastModified": "ISO date string",
          "currentVersion": "string",
          "id": "TitleName3"
      }
  ]
  ```

- `/software/TitleName1,TitleName2` : Returns a subset of patch titles. The titles must have their IDs passed in a comma separated string as shown. The returned data is the same as the `/software` endpoint.

  ```json
  [
      {
          "name": "string",
          "publisher": "string",
          "lastModified": "ISO date string",
          "currentVersion": "string",
          "id": "TitleName1"
      },
      {
          "name": "string",
          "publisher": "string",
          "lastModified": "ISO date string",
          "currentVersion": "string",
          "id": "TitleName2"
      }
  ]
  ```

- `/patch/TitleName` : Returns the full JSON patch definition for the provided patch title ID (see Jamf's documentation for more details on the patch title schema).

  ```json
  {
      "name": "string",
      "publisher": "string",
      "appName": "string",
      "bundleId": "string",
      "lastModified": "ISO date string",
      "currentVersion": "string",
      "requirements": ["Array of Requirement Objects"],
      "patches": ["Array of Patch Objects"],
      "extensionAttributes": ["Array of Extension Attribute Objects"],
      "id": "TitleName"
  }
  ```

Each endpoint's full URL would be entered into your browser as:

```text
https://<site-name>.netlify.app/software
https://<site-name>.netlify.app/software/TitleName1,TitleName2
https://<site-name>.netlify.app/patch/TitleName
```
