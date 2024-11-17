
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
2. Add your bot token and webhook URL:

   ```json
   bot_token: "YOUR_BOT_TOKEN"
   webhook_url: "YOUR_WEBHOOK_URL"  # Optional
   ```


## Commands

Riese Bot offers a variety of commands:

**Basic Commands:**

* `/ping`: Checks the bot's latency.
* `/say`: Makes the bot say something.
* `/afk`: Set your AFK status.
* `/help`: Shows this help message.


**Admin Commands:**

* `/role add`: Add a role to a user.
* `/role remove`: Remove a role from a user.
* `/role list`: Show role list of a user.
* `/kick`: Kick a user.
* `/ban`: Ban a user.
* `/unban`: Unban a user.
* `/warn`: warn a user
* `/warn remove` remove warn from a user
* `/warn list` See the warn list

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
