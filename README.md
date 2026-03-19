# Estrutura de Condomínio WebApp 🏢

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat&logo=python)
![Django](https://img.shields.io/badge/Backend-Django-092E20?style=flat&logo=django)
![HTML5](https://img.shields.io/badge/Frontend-HTML5-E34F26?style=flat&logo=html5)

Interface web para prestação de serviços em condomínios. A interface permite que você gere uma estrutura que abre uma entrada para cada apartamento, onde se pode fazer upload de documentos e mídia. Dessa forma a documentação dos serviços prestados a um condomínio fica organizada e padronizada para download e acesso.

É possível ter diferentes pessoas acessando e alimentando a estrutura, com autenticação baseada em permissões. Nesse caso criei esse protótipo para facilitar o serviço de conversão de equipamentos de gás para a empresa em que trabalho.

## 📱 Screenshots

*(Add your screenshots here! Create a `docs/images/` folder in your repo, drop the images in, and update these links.)*

| Dashboard | Mobile View | Data Visualization |
| :---: | :---: | :---: |
| <img src="docs/images/dashboard.png" width="250"/> | <img src="docs/images/mobile.png" width="250"/> | <img src="docs/images/charts.png" width="250"/> |

## ✨ Key Features

* **Secure User Authentication:** Controlled access ensures that user data and conversion histories remain private and protected within the system.
* **Interactive Data Visualization:** Clean, readable visual representations of the processed data to easily track metrics and conversion outputs.
* **Mobile-Friendly Layout:** A fully responsive HTML/CSS frontend interface that automatically adapts to provide a flawless experience on both desktop monitors and smartphones.
* **Secure Configuration:** strict environment variable management to shield sensitive credentials and database keys from public exposure.

## 💻 Tech Stack

* **Backend Framework:** Django (Python)
* **Frontend:** HTML5, CSS3
* **Security:** `python-dotenv` for environment variable management

## 🗺️ Repository Structure

```plaintext
├── starter/                  # Main Django project and application files
│   ├── manage.py             # Django execution script
│   └── ...                   
├── .env.example              # Template for required environment variables
├── .gitignore                # Security and cache exclusions
├── requirements.txt          # Python dependencies
└── README.md