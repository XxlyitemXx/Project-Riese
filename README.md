
<a name="readme-top"></a>

# Riese Discord Bot

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<br />
<div align="center">
  <a href="https://github.com/xxlyitemxx/project-reise">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>


<h3 align="center">Riese Bot</h3>

  <p align="center">
    A versatile Discord bot with moderation, utility.
    <br />
    <a href="https://github.com/xxlyitemxx/project-reise"><strong>Explore the Code »</strong></a>
    <br />
    <br />
    <a href="https://github.com/xxlyitemxx/project-reise/issues/new?labels=bug">Report Bug</a>
    ·
    <a href="https://github.com/xxlyitemxx/project-reise/issues/new?labels=enhancement">Request Feature</a>
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
   git clone https://github.com/xxlyitemxx/project-reise.git
   ```
2. Navigate to the project directory:
   ```bash
   cd project-reise
   ```
3. Install the required libraries:
   ```bash
   pip install -r requirements.txt 
   ```

### Configuration

1. Create a `config.json` file in the root directory.
2. Add your bot token and other configuration:

   ```json
   {
     "token": "YOUR_DISCORD_BOT_TOKEN",
     "prefix": "?",
     "api_keys_gemini": [
       "YOUR_GEMINI_API_KEY_1",
       "YOUR_GEMINI_API_KEY_2",
       "YOUR_GEMINI_API_KEY_3"
     ]
   }
   ```

#### Multi-API Key Support

Riese now supports multiple API keys for the Gemini AI service. This feature helps handle rate limiting by automatically switching to the next available API key when one reaches its quota limit. To use this feature:

1. Add multiple API keys in the `api_keys_gemini` array in your `config.json` file.
2. The bot will automatically rotate through these keys when it encounters rate limit errors (HTTP 429).
3. Use the `?api_keys` command to view the usage statistics of your API keys.

This feature ensures uninterrupted AI service even when individual API keys reach their quota limits.

## Commands

Riese Bot offers a comprehensive set of commands to enhance your Discord server:

### Basic Commands

* `/ping`: Checks the bot's latency with status indicator.
* `/say [message]`: Makes the bot say something.
* `/help`: Shows all available commands.
* `/avatar [user]`: Displays a user's avatar in full size.
* `/count member`: Shows detailed server member count with status breakdown.
* `/invite`: Get the bot's invite link.
* `/about me`: Displays information about Reise bot.
* `?help`: Alternative command to show all available commands.

### User Status Commands

* `/afk [message]`: Set your AFK status with optional custom message.
* `?afk [message]`: Alternative command for setting AFK status.
* `?w [member]`: Show detailed member information.

### Moderation Commands

* `/ban [user] [reason]`: Ban a user from the server.
* `/unban [user_id] [reason]`: Unban a previously banned user.
* `/kick [user] [reason]`: Kick a user from the server.
* `/clear [amount]`: Delete a specified number of messages.
* `?clear [amount]`: Alternative command for clearing messages.

### Warning System

* `/warn add [user] [reason]`: Issue a warning to a user.
* `/warn remove [user]`: Remove a warning from a user.
* `/warn list`: View all active warnings in the server.

### Role Management

* `/role add [user] [role]`: Add a role to a user.
* `/role remove [user] [role]`: Remove a role from a user.
* `/role list [user]`: Display all roles a user has.

### Group Chat Commands

* `/gc setup [gc-name]`: Create a new group chat.
* `/gc add-member [gc-name] [member]`: Add a member to a group chat.
* `/gc remove-member [gc-name] [member]`: Remove a member from a group chat.
* `/gc delete [gc-name]`: Delete a group chat.
* `/gc toggle`: Enable or disable group chat functionality.
* `/gc rename [gc-name] [new-name]`: Rename an existing group chat.
* `/gc admin [gc-name] [member]`: Grant admin permissions to a member.
* `/gc leave [gc-name]`: Leave a group chat.
* `?gc setup [gc-name]`: Alternative command for creating a group chat.

### Trigger System

* `/trigger`: Manage automatic responses to trigger words.
* `/trigger add`: Add a new trigger word and response.
* `/trigger list`: View all configured trigger words.

### AI Commands

* `?sy [text]`: Summarize text with AI assistance.
* `?ask [question]`: Ask a question to the AI.

### Utility Commands

* `/avatar [user]`: Show a user's avatar.
* `/invite`: Get an invite link for Riese.

<!-- CONTRIBUTING -->
## Contributing

Contributions are welcome!  Fork the repository, make your changes, and submit a pull request.


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


<!-- CONTACT -->
## Contact


Project Link: [https://github.com/xxlyitemxx/project-reise](https://github.com/xxlyitemxx/project-reise)




<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/xxlyitemxx/project-reise.svg?style=for-the-badge
[contributors-url]: https://github.com/xxlyitemxx/project-reise/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/xxlyitemxx/project-reise.svg?style=for-the-badge
[forks-url]: https://github.com/xxlyitemxx/project-reise/network/members
[stars-shield]: https://img.shields.io/github/stars/xxlyitemxx/project-reise.svg?style=for-the-badge
[stars-url]: https://github.com/xxlyitemxx/project-reise/stargazers
[issues-shield]: https://img.shields.io/github/issues/xxlyitemxx/project-reise.svg?style=for-the-badge
[issues-url]: https://github.com/xxlyitemxx/project-reise/issues
[license-shield]: https://img.shields.io/github/license/xxlyitemxx/project-reise.svg?style=for-the-badge
[license-url]: https://github.com/xxlyitemxx/project-reise/blob/master/LICENSE.txt
