from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import os
import fitz
from sentence_transformers import SentenceTransformer, util
import spacy
import re


# ✅ Load spaCy model with sentencizer
nlp = spacy.load("en_core_web_sm")
if not nlp.has_pipe("sentencizer"):
    nlp.add_pipe("sentencizer")


# ✅ Load Sentence-BERT model
model = SentenceTransformer('output/job_bert')


# ✅ Sentence splitter using spaCy
def get_smart_sentences(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 5]


# ✅ Clean each sentence for embedding
def clean_sentence(sentence):
    sentence = sentence.replace('\n', ' ').strip()
    sentence = re.sub(r'\s+', ' ', sentence)
    sentence = re.sub(r'[^\w\s.,;!?/-]', '', sentence)
    return sentence


# ✅ NEW: Bidirectional semantic similarity
def get_avg_similarity_bidirectional(text1, text2):
    sentences1 = [clean_sentence(s) for s in get_smart_sentences(text1)]
    sentences2 = [clean_sentence(s) for s in get_smart_sentences(text2)]

    if not sentences1 or not sentences2:
        return 0.0, [], []

    embeddings1 = model.encode(sentences1, convert_to_tensor=True)
    embeddings2 = model.encode(sentences2, convert_to_tensor=True)

    cosine_scores = util.cos_sim(embeddings1, embeddings2)

    # 🔁 Resume ➝ JD
    r2j_best = cosine_scores.max(dim=1).values
    r2j_score = r2j_best.mean().item()

    # 🔁 JD ➝ Resume
    j2r_best = cosine_scores.max(dim=0).values
    j2r_score = j2r_best.mean().item()

    # 🧠 Final bidirectional score
    final_score = (r2j_score + j2r_score) / 2

    # 🧾 Match report (from Resume ➝ JD only)
    indices = cosine_scores.max(dim=1).indices
    match_report = []
    for i, score in enumerate(r2j_best):
        match_report.append({
            'resume_sentence': sentences1[i],
            'matched_jd_sentence': sentences2[indices[i]],
            'score': round(score.item() * 100, 2)
        })

    return round(final_score * 100, 2), sentences1, match_report


# ✅ Extract text from PDF, image, txt
def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        doc = fitz.open(file_path)
        return " ".join(page.get_text() for page in doc)
    elif ext in [".jpg", ".png"]:
        from PIL import Image
        import pytesseract
        return pytesseract.image_to_string(Image.open(file_path))
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# ✅ Basic cleanup
def clean_text(text):
    return text.replace('\n', ' ').strip()


# ✅ NEW: Extract matched keywords between resume and JD
def extract_matched_keywords(resume_text, jd_text, min_score=0.7):
    """Extract keywords that appear in both resume and JD with high semantic similarity"""
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        
        try:
            stop_words = set(stopwords.words('english'))
        except:
            # Download stopwords if not available
            try:
                nltk.download('stopwords', quiet=True)
                nltk.download('punkt', quiet=True)
                stop_words = set(stopwords.words('english'))
            except:
                stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        
        # Extract meaningful words (3+ chars, not stopwords)
        try:
            resume_words = [word.lower() for word in word_tokenize(resume_text) 
                           if len(word) > 2 and word.isalpha() and word.lower() not in stop_words]
            jd_words = [word.lower() for word in word_tokenize(jd_text) 
                       if len(word) > 2 and word.isalpha() and word.lower() not in stop_words]
        except:
            # Fallback to simple split if NLTK tokenizer fails
            resume_words = [word.lower().strip('.,!?;:') for word in resume_text.split() 
                           if len(word) > 2 and word.isalpha() and word.lower() not in stop_words]
            jd_words = [word.lower().strip('.,!?;:') for word in jd_text.split() 
                       if len(word) > 2 and word.isalpha() and word.lower() not in stop_words]
    except ImportError:
        # Fallback if NLTK is not available
        stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        resume_words = [word.lower().strip('.,!?;:') for word in resume_text.split() 
                       if len(word) > 2 and word.isalpha() and word.lower() not in stop_words]
        jd_words = [word.lower().strip('.,!?;:') for word in jd_text.split() 
                   if len(word) > 2 and word.isalpha() and word.lower() not in stop_words]
    
    # Find common words
    common_words = list(set(resume_words) & set(jd_words))
    
    # Add some domain-specific keywords if found
    tech_keywords = ['python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'django', 'flask',
                    'sql', 'mysql', 'postgresql', 'mongodb', 'aws', 'azure', 'docker', 'kubernetes',
                    'machine learning', 'data science', 'artificial intelligence', 'deep learning']
    
    for keyword in tech_keywords:
        if keyword in resume_text.lower() and keyword in jd_text.lower():
            common_words.append(keyword)
    
    return list(set(common_words))[:15]  # Return top 15 unique keywords


# ✅ NEW: Multi-resume comparison function
def compare_multiple_resumes(resumes_data, jd_text):
    """Compare multiple resumes against a job description"""
    results = []
    
    for resume_name, resume_text in resumes_data:
        if len(resume_text.strip()) < 20:
            continue
            
        # Get semantic similarity score
        score, _, match_report = get_avg_similarity_bidirectional(resume_text, jd_text)
        
        # Extract matched keywords
        matched_keywords = extract_matched_keywords(resume_text, jd_text)
        
        results.append({
            'resume_name': resume_name,
            'score': score,
            'matched_keywords': matched_keywords,
            'match_report': match_report[:5]  # Top 5 matches only
        })
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results


# ✅ Extract only job-relevant lines (skills, projects, etc.)
def extract_relevant_text(text):
    keywords = ['skills', 'projects', 'experience', 'responsibilities', 'requirements']
    lines = text.splitlines()
    relevant = [line for line in lines if any(k in line.lower() for k in keywords) or len(line.split()) > 5]
    filtered = " ".join(relevant)
    return filtered if len(filtered.split()) >= 50 else text


# ✅ Upload form view (original single resume)
def upload_view(request):
    return render(request, 'analysis/upload.html')


# ✅ Upload form view for multi-resume
def multi_upload_view(request):
    return render(request, 'analysis/multi_upload.html')


# ✅ NEW: Multi-resume match endpoint
@csrf_exempt
def multi_match_view(request):
    if request.method == 'POST':
        jd_file = request.FILES.get('jd')
        
        if not jd_file:
            return JsonResponse({'error': 'Job description file is required'}, status=400)
        
        # Collect resume files
        resume_files = []
        for i in range(1, 6):  # resume1 to resume5
            resume_file = request.FILES.get(f'resume{i}')
            if resume_file:
                resume_files.append(resume_file)
        
        if not resume_files:
            return JsonResponse({'error': 'At least one resume file is required'}, status=400)
        
        try:
            # Save and process JD
            jd_path = default_storage.save(f"jds/{jd_file.name}", jd_file)
            jd_text_raw = extract_text(os.path.join("media", jd_path))
            jd_text = clean_text(extract_relevant_text(jd_text_raw))
            
            if len(jd_text) < 50:
                return JsonResponse({'error': 'Job description content is too short or unreadable'}, status=400)
            
            # Process resumes
            resumes_data = []
            resume_paths = []
            
            for resume_file in resume_files:
                resume_path = default_storage.save(f"resumes/{resume_file.name}", resume_file)
                resume_paths.append(resume_path)
                
                resume_text_raw = extract_text(os.path.join("media", resume_path))
                resume_text = clean_text(extract_relevant_text(resume_text_raw))
                
                if len(resume_text) >= 50:  # Only process if sufficient content
                    resumes_data.append((resume_file.name, resume_text))
            
            if not resumes_data:
                return JsonResponse({'error': 'No valid resume content found'}, status=400)
            
            # Compare all resumes
            results = compare_multiple_resumes(resumes_data, jd_text)
            
            # Clean up uploaded files
            default_storage.delete(jd_path)
            for resume_path in resume_paths:
                default_storage.delete(resume_path)
            
            return JsonResponse({
                'success': True,
                'results': results,
                'total_resumes': len(results)
            })
            
        except Exception as e:
            # Clean up files in case of error
            try:
                default_storage.delete(jd_path)
                for resume_path in resume_paths:
                    default_storage.delete(resume_path)
            except:
                pass
            
            return JsonResponse({'error': f'Processing error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# ✅ Main match endpoint
@csrf_exempt
def match_view(request):
    if request.method == 'POST':
        resume_file = request.FILES.get('resume')
        jd_file = request.FILES.get('jd')

        if not resume_file or not jd_file:
            return JsonResponse({'error': 'Both resume and JD files are required'}, status=400)

        # Save uploaded files
        resume_path = default_storage.save(f"resumes/{resume_file.name}", resume_file)
        jd_path = default_storage.save(f"jds/{jd_file.name}", jd_file)

        resume_text_raw = extract_text(os.path.join("media", resume_path))
        jd_text_raw = extract_text(os.path.join("media", jd_path))

        resume_text = clean_text(extract_relevant_text(resume_text_raw))
        jd_text = clean_text(extract_relevant_text(jd_text_raw))

        if len(resume_text) < 50 or len(jd_text) < 50:
            return JsonResponse({'match_percentage': 0.0, 'warning': 'Too little meaningful content'}, status=200)

        # 🔁 Bidirectional semantic similarity
        semantic_score, _, match_report = get_avg_similarity_bidirectional(resume_text, jd_text)
        final_score = semantic_score

        # Delete uploaded files
        default_storage.delete(resume_path)
        default_storage.delete(jd_path)

        return JsonResponse({
            'final_score': final_score,
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)
