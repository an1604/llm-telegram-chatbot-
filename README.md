# Telegram Chatbot with Integrated LLM and Automated Active Learning

This repository features a Telegram chatbot powered by an integrated Language Learning Model (LLM) that employs advanced active learning techniques. The chatbot dynamically updates its knowledge base by leveraging user feedback and automated machine learning models to predict the correctness of its responses. Designed for continuous self-improvement, the bot provides increasingly accurate and context-aware interactions over time.

## Features

- **Integrated Language Learning Model (LLM)**: Uses a sophisticated LLM to generate context-aware responses, providing meaningful and relevant interactions.
- **Embedding Model with RAG Techniques**: Applies an embedding model using [sentence-transformers](https://www.sbert.net/) to create dense vector representations of user inputs. This is used in conjunction with Retrieval-Augmented Generation (RAG) techniques to enhance the relevance of the responses by retrieving relevant information from a knowledge base before generating a response.
- **Automated Active Learning**: Leverages active learning techniques to continuously improve the model's performance based on user feedback and automated evaluations.
- **Dynamic Knowledge Base Updates**: Continuously updates the knowledge base by incorporating new information and feedback, ensuring that the chatbot provides accurate and up-to-date responses.
- **Telegram Integration**: Seamlessly connects with Telegram to provide real-time, interactive chat capabilities.


## Technology Stack

The chatbot is built using the following technologies:

- ![Aiogram](https://img.shields.io/badge/Aiogram-000000?style=for-the-badge) - A powerful Python framework for building Telegram bots.
- ![Asyncio](https://img.shields.io/badge/Asyncio-0000FF?style=for-the-badge) - A Python library for writing concurrent code using the async/await syntax.
- ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white) - A deep learning framework for building and training machine learning models.
- ![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFCA28?style=for-the-badge&logo=huggingface&logoColor=black) - A platform providing state-of-the-art NLP models and tools.


## Getting Started

To set up and run the Telegram chatbot, follow these steps:

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/yourusername/telegram-chatbot-active-learning.git
   ```

2. **Navigate to the project directory**:  
   Change the current directory to where the project files are located by running:  
   ```bash
   cd telegram-chatbot-active-learning
   ```

3. **Install the required dependencies**:  
   Ensure you have Python installed, then run the following command to install all necessary dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot token**:  
   Obtain a bot token from [BotFather](https://t.me/BotFather) on Telegram and set it as an environment variable:  
   ```bash
   export TELEGRAM_TOKEN='your-telegram-token'
   ```

5. **Run the chatbot server**:  
   Start the chatbot by running the following command:  
   ```bash
   python chatbot_server.py
   ```
