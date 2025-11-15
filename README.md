# EduMentor AI

A comprehensive AI-powered e-learning platform that generates complete learning materials instantly from any topic. Built with Flask and modern web technologies.

## Features

### 🎓 Student Features
- **Study Notes**: Generate comprehensive study notes on any topic
- **Summaries**: Create concise summaries for quick review
- **Quizzes**: Generate interactive quizzes with multiple-choice questions
- **Flashcards**: Create digital flashcards for memorization
- **Diagrams**: Get descriptions for visual learning aids
- **Video Scripts**: Generate scripts for educational videos
- **Doubt Solver**: AI-powered question answering
- **Progress Tracking**: Track your learning progress and scores
- **Adaptive Learning**: Personalized difficulty based on performance

### 👨‍🏫 Teacher Features
- **Lesson Plans**: Generate detailed lesson plans with objectives and activities
- **Homework**: Create homework assignments with answer keys
- **Assessments**: Generate tests and quizzes for students

### 📤 Export Options
- Export content as **PDF**
- Export content as **Word Document (DOCX)**
- Export content as **PowerPoint (PPT)**

### 🌍 Multilingual Support
- Support for multiple languages (English, Spanish, French, German, Hindi, and more)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "pro 2"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up OpenAI API Key (Optional but Recommended)**
   
   For full AI functionality, you need an OpenAI API key:
   - Get your API key from [OpenAI](https://platform.openai.com/api-keys)
   - Set it as an environment variable:
     - Windows (PowerShell):
       ```powershell
       $env:OPENAI_API_KEY="your-api-key-here"
       ```
     - Windows (CMD):
       ```cmd
       set OPENAI_API_KEY=your-api-key-here
       ```
     - macOS/Linux:
       ```bash
       export OPENAI_API_KEY="your-api-key-here"
       ```
   
   **Note**: The app will work without an API key but will use mock responses for demonstration purposes.

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:5000`

## Project Structure

```
pro 2/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── modules/              # Custom modules
│   ├── __init__.py
│   ├── ai_generator.py   # AI content generation
│   ├── export_manager.py # Export functionality
│   └── progress_tracker.py # Progress tracking
├── templates/            # HTML templates
│   └── index.html        # Main page
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Stylesheet
│   └── js/
│       └── main.js       # Frontend JavaScript
├── exports/              # Generated export files (created automatically)
└── edumentor.db          # SQLite database (created automatically)
```

## Usage

### Generating Content

1. **Enter a topic** in the topic input field
2. **Select content type** (Notes, Summary, Quiz, Flashcards, etc.)
3. **Choose difficulty level** (Easy, Medium, Hard)
4. **Select language** (if needed)
5. **Click "Generate Content"**

### Taking Quizzes

1. Enter a topic and number of questions
2. Click "Generate Quiz"
3. Click on answer options to see correct/incorrect feedback
4. View explanations for each question

### Using Flashcards

1. Enter a topic and number of cards
2. Click "Generate Flashcards"
3. Click on any card to flip it and see the answer

### Exporting Content

1. Generate any content first
2. Click one of the export buttons (PDF, DOCX, PPT)
3. The file will download automatically

### Teacher Tools

1. Use the "Lesson Plan" section to generate lesson plans
2. Use the "Homework" section to create assignments
3. Both include detailed instructions and answer keys

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for AI functionality
- `SECRET_KEY`: Flask secret key (defaults to dev key, change in production)

### Database

The application uses SQLite by default. The database file (`edumentor.db`) is created automatically on first run.

## API Endpoints

- `POST /generate` - Generate learning content
- `POST /quiz` - Generate quiz
- `POST /flashcards` - Generate flashcards
- `POST /doubt-solve` - Solve student doubts
- `POST /export` - Export content
- `GET /progress` - Get user progress
- `POST /progress` - Update user progress
- `POST /lesson-plan` - Generate lesson plan
- `POST /homework` - Generate homework

## Troubleshooting

### Common Issues

1. **Module not found errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`

2. **API errors**
   - Check if your OpenAI API key is set correctly
   - The app works with mock data if no API key is provided

3. **Export errors**
   - Make sure the `exports/` directory exists and is writable
   - Check that all export libraries are installed

4. **Database errors**
   - Delete `edumentor.db` and restart the app to recreate the database

## Development

### Adding New Features

The codebase is modular and easy to extend:

- **AI Generation**: Add new content types in `modules/ai_generator.py`
- **Export Formats**: Add new formats in `modules/export_manager.py`
- **UI Components**: Modify templates and static files

### Code Style

- Follow PEP 8 Python style guide
- Use clear, descriptive variable names
- Add comments explaining complex logic
- Keep functions small and focused

## License

This project is open source and available for educational purposes.

## Support

For issues or questions, please check the code comments or create an issue in the repository.

---

**Built with ❤️ using Flask and AI**

