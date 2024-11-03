```markdown
<a name="readme-top"></a>

# Riese Discord Bot

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]


<br />
<div align="center">


<h3 align="center">Riese Bot</h3>

  <p align="center">
    A versatile Discord bot with moderation, utility, and welcome features.
    <br />
    <a href="https://github.com/your_github_username/your_repo_name"><strong>Explore the Code »</strong></a>
    <br />
    <br />
    <a href="https://github.com/your_github_username/your_repo_name/issues/new?labels=bug">Report Bug</a>
    ·
    <a href="https://github.com/your_github_username/your_repo_name/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#configuration">Configuration</a></li>
      </ul>
    </li>
 <li><a href="#commands">Commands</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>

  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project


Riese is a Discord bot designed to enhance your server's functionality.  It offers a range of features, including moderation tools, utility commands, and welcome messages for new members.  The bot is built using Python and the `nextcord` library.




### Built With

* [Python](https://www.python.org/)
* [nextcord](https://guide.nextcord.dev/)
* [SQLite](https://www.sqlite.org/index.html)


<!-- GETTING STARTED -->
## Getting Started


### Prerequisites

* Python 3.8 or higher
* `nextcord` library
* A Discord bot token

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your_github_username/your_repo_name.git
   ```
2. Navigate to the project directory:
   ```bash
   cd your_repo_name
   ```
3. Install the required libraries:
   ```bash
   pip install -r requirements.txt 
   ```

### Configuration

1. Create a `config.yaml` file in the root directory.
2. Add your bot token and webhook URL:

   ```yaml
   bot_token: "YOUR_BOT_TOKEN"
   webhook_url: "YOUR_WEBHOOK_URL"  # Optional
   ```


## Commands

Riese Bot offers a variety of commands:

**Basic Commands:**

* `/ping`: Checks the bot's latency.
* `/say`: Makes the bot say something.
* `/invite`: Get the bot's invite link.
* `/about`: Information about the bot.
* `/partner`: See our partner servers.
* `/avatar`: Get a user's avatar.
* `/count_messages`: Server's message count.
* `/count_member`: View the member count.
* `/afk`: Set your AFK status.
* `/help`: Shows this help message.


**Admin Commands:**

* `/role_add`: Add a role to a user.
* `/summon`:  DM a user and mention them (Admin only).
* `/kick`: Kick a user.
* `/ban`: Ban a user.
* `/clear`: Clear messages.
* `/unban`: Unban a user.
* `/role_remove`: Remove a role from a user.
* `/nickname`: Change a user's nickname.

**Anti-Raid Commands:**

* `/anti_raid`: Toggle anti-raid on/off (Admin only).
* `/antiraid_disablechannel`: Disable anti-raid in a channel (Admin only).
* `/warn_list`: See the warn list (Admin only).
* `/remove_warn`: Remove a warn from a user (Admin only).

**Welcome Commands:**

* `/welcome_channel`: Set the welcome channel and message (Admin only).


<!-- CONTRIBUTING -->
## Contributing

Contributions are welcome!  Fork the repository, make your changes, and submit a pull request.


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.


<!-- CONTACT -->
## Contact


Project Link: [https://github.com/your_github_username/your_repo_name](https://github.com/your_github_username/your_repo_name)




<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/your_github_username/your_repo_name.svg?style=for-the-badge
[contributors-url]: https://github.com/your_github_username/your_repo_name/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/your_github_username/your_repo_name.svg?style=for-the-badge
[forks-url]: https://github.com/your_github_username/your_repo_name/network/members
[stars-shield]: https://img.shields.io/github/stars/your_github_username/your_repo_name.svg?style=for-the-badge
[stars-url]: https://github.com/your_github_username/your_repo_name/stargazers
[issues-shield]: https://img.shields.io/github/issues/your_github_username/your_repo_name.svg?style=for-the-badge
[issues-url]: https://github.com/your_github_username/your_repo_name/issues
[license-shield]: https://img.shields.io/github/license/your_github_username/your_repo_name.svg?style=for-the-badge
[license-url]: https://github.com/your_github_username/your_repo_name/blob/master/LICENSE.txt
