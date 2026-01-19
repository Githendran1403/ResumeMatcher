Multi-Resume Job Matcher
Features
This enhanced resume analyzer allows you to:

🔥 NEW: Multi-Resume Comparison
Upload up to 5 resumes at once
Compare all resumes against a single job description
Get ranking of candidates based on match percentage
View detailed analysis for each resume
See matched keywords between resumes and job description
🎯 Smart Analysis
Bidirectional semantic similarity using Sentence-BERT
Keyword extraction and matching
Interactive UI with progress bars and rankings
Real-time results with smooth animations
How to Use
1. Access the Multi-Resume Matcher
http://localhost:8000/multi/
2. Upload Files
Job Description: Upload one JD file (required)
Resumes: Upload 1-5 resume files
Supported formats: PDF, DOCX, TXT, PNG, JPG
At least one resume is required
3. View Results
Rankings: See resumes ranked by match percentage
Detailed Analysis: View individual scores and matched keywords
Visual Progress: Color-coded progress bars (green/yellow/red)
File Structure
analysis/
├── templates/
│   ├── analysis/
│   │   ├── upload.html          # Single resume matcher
│   │   └── multi_upload.html    # NEW: Multi-resume matcher
├── views.py                     # Enhanced with multi-resume logic
└── urls.py                      # Added /multi/ and /multi-match/ routes
API Endpoints
Single Resume (Original)
GET / - Upload form
POST /match/ - Analyze single resume
Multi-Resume (NEW)
GET /multi/ - Multi-upload form
POST /multi-match/ - Analyze multiple resumes
Dependencies
Make sure you have installed:

pip install nltk
Run once to download NLTK data:

python download_nltk_data.py
Response Format (Multi-Resume)
{
  "success": true,
  "total_resumes": 3,
  "results": [
    {
      "resume_name": "john_doe.pdf",
      "score": 85.2,
      "matched_keywords": ["python", "django", "sql", "aws"],
      "match_report": [...]
    },
    {
      "resume_name": "jane_smith.pdf", 
      "score": 78.9,
      "matched_keywords": ["javascript", "react", "node"],
      "match_report": [...]
    }
  ]
}
Features in Detail
🏆 Ranking System
Resumes are automatically ranked by match percentage
Visual indicators for performance levels:
Green (70%+): Excellent match
Yellow (50-69%): Good match
Red (<50%): Poor match
🔍 Keyword Analysis
Extracts common keywords between resume and JD
Includes domain-specific technology keywords
Shows top 10 matched keywords per resume
Uses NLTK for advanced text processing
💫 Enhanced UI
Modern Bootstrap 5 design
Smooth animations and transitions
Responsive for mobile devices
Loading states and error handling
Usage Tips
Quality: Ensure resume files have clear, readable text
Format: PDF and DOCX work best for text extraction
Content: More detailed resumes typically get better analysis
JD Length: Longer job descriptions provide better matching context
Troubleshooting
Common Issues
"Too little meaningful content": File may be corrupted or have insufficient text
NLTK errors: Run python download_nltk_data.py to fix missing data
Model loading slow: First load takes time due to Sentence-BERT initialization
Performance Notes
First request may take 30-60 seconds (model loading)
Subsequent requests are much faster
Processing time increases with number of resumes
