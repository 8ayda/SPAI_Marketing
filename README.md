# ⚽️ SPAI-Marketing

**SPAI-Marketing** (Sponsorship Performance AI) is an AI-powered platform designed to evaluate sponsor logo visibility in professional football match footage. Built with modularity and scalability in mind, this system combines state-of-the-art computer vision techniques with real-time data analytics to deliver meaningful insights for sports marketing stakeholders.

---
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)  ![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white) ![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)  ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)  ![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black) ![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white) ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white) 

---

## 📽️ Demo

Check out a demo video of SPAI-Marketing in action:  
👉 [Watch the Demo](https://youtu.be/KZc_jdVGWso)  


## 🔍 Overview

This project integrates several key components:

- 🎯 **YOLOv8-based Logo Detection**  
  Trained to identify and locate sponsor logos on football kits with high precision using annotated match frames.

- 📊 **Sponsorship KPI Engine**  
  Custom logic to quantify sponsor exposure based on screen position, visibility level, and logo size throughout the match.

- 🎥 **Video Processing Pipeline**  
  Built with OpenCV and DeepSORT for object tracking across frames, enabling logo visibility aggregation over time.

- 🌐 **Interactive Dashboard**  
  A Plotly Dash-based frontend that displays game-specific visibility metrics, dynamic graphs, and aggregated reports for each sponsor.

- 🗃️ **Database Integration**  
  Uses Supabase (PostgreSQL) to manage uploaded games, sponsor metadata, and analysis results across the platform.

## 🚀 Features

- Logo detection powered by YOLOv8  
- Real-time logo tracking and visibility scoring  
- Sponsor exposure metrics (duration, size, screen position)  
- Match-specific dashboards  
- Admin interface for uploading game videos and metadata  
- Seamless backend/frontend communication via FastAPI  
- Scalable pipeline adaptable to other sports or media assets


## 🛠️ Technologies Used

- Python (YOLOv8, OpenCV, FastAPI)
- Plotly Dash (Frontend)
- Supabase (PostgreSQL DB)
- Google Colab (Model Training)
- Roboflow (Annotation & Dataset Management)

## 📁 Project Structure

```bash
SPAI-Marketing/
│
├── Notebooks/              # Google Colab notebooks for training, inference, testing
├── SPAI_admin/             # Admin dashboard (Dash + FastAPI integration)
├── SPAI_client/            # Client dashboard to visualize sponsor metrics
├── .gitignore              # Git configuration
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
