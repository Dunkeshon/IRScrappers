# IKEA Hacks Information Retrieval System

## Overview
An information retrieval system for exploring IKEA-related content, combining a Django-powered backend with a React and Tailwind CSS frontend. Features include results snippets, user feedback with dynamic relevance updates, and results clustering for seamless navigation.

## Features
- **Results Snippets**: Concise summaries for articles; full-text display for reviews.
- **User Feedback**: Dynamic relevance adjustments with real-time result reordering.
- **Results Clustering**: Organized results into categories like "Articles" and "Reviews."

![ikea_gif](https://github.com/user-attachments/assets/5a7b5d4f-e8ff-4ef1-b643-fbf40e97e578)

## Tech Stack
- **Backend**: Django, PyTerrier
- **Frontend**: React, Tailwind CSS
- **Database**: MongoDB (optional for preprocessing)

## Installation
1. **Backend**:
   - Install dependencies:
     ```bash
     pip install django djangorestframework python-terrier pandas nltk django-cors-headers
     ```
   - Navigate to `backend`:
     ```bash
     cd backend
     ```
   - Run migrations:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```
   - Start the server:
     ```bash
     python manage.py runserver
     ```

2. **Frontend**:
   - Navigate to `ikea_search`:
     ```bash
     cd ikea_search
     ```
   - Install dependencies:
     ```bash
     npm install
     ```
   - Start the server:
     ```bash
     npm start
     ```

## Usage
- Access the app at `http://localhost:3000`.

Make sure you have both frontend and backend running in two terminals.
