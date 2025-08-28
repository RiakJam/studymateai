# import requests
# from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
# import mysql.connector, hashlib
# import re, logging, random, string
# from datetime import datetime, timedelta
# import json

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# app.secret_key = "supersecretkey"

# # Paystack configuration (only secret key needed for verification)
# PAYSTACK_SECRET_KEY = "sk_test_34d568ac6ea779fe94bafe563e481b7c163dfcb0"

# # Database configuration
# def get_db_connection():
#     try:
#         conn = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="hackerthone_db"
#         )
#         return conn
#     except mysql.connector.Error as err:
#         logger.error(f"Database connection failed: {err}")
#         return None

# # ---------------- PAYMENT PROCESSOR CLASS ----------------
# class PaymentProcessor:
#     def __init__(self):
#         self.headers = {
#             'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
#             'Content-Type': 'application/json'
#         }
    
#     def verify_transaction(self, reference):
#         """
#         Verify a Paystack transaction - SIMULATED FOR TESTING
#         """
#         try:
#             # For testing, simulate a successful response
#             simulated_response = {
#                 'status': True,
#                 'message': 'Verification successful',
#                 'data': {
#                     'status': 'success',
#                     'reference': reference,
#                     'amount': 10000,  # Example amount in Kobo
#                     'currency': 'KES',
#                     'metadata': {
#                         'plan_type': 'premium',
#                         'duration_months': 1,
#                         'user_id': 1
#                     }
#                 }
#             }
#             return simulated_response
                
#         except Exception as e:
#             print(f"Error verifying transaction: {e}")
#             return None
    
#     def handle_webhook(self, payload):
#         """
#         Handle webhook events from Paystack - MODIFIED FOR INSTANT PROCESSING
#         """
#         try:
#             # For testing, accept any payload and process immediately
#             if isinstance(payload, bytes):
#                 payload = payload.decode('utf-8')
            
#             # Try to parse as JSON, but if it fails, create a simulated event
#             try:
#                 event = json.loads(payload)
#             except json.JSONDecodeError:
#                 # Create a simulated successful payment event for testing
#                 event = {
#                     'event': 'charge.success',
#                     'data': {
#                         'reference': 'test_ref_' + datetime.now().strftime('%Y%m%d%H%M%S'),
#                         'amount': 10000,
#                         'metadata': {
#                             'plan_type': 'premium',
#                             'duration_months': 1,
#                             'user_id': 1
#                         }
#                     }
#                 }
            
#             # Process any event as successful for testing
#             data = event.get('data', {})
#             reference = data.get('reference', 'test_ref_' + datetime.now().strftime('%Y%m%d%H%M%S'))
            
#             # Extract metadata with defaults for testing
#             metadata = data.get('metadata', {})
#             plan_type = metadata.get('plan_type', 'premium')
#             duration_months = int(metadata.get('duration_months', 1))
#             user_id = int(metadata.get('user_id', 1))
#             amount = data.get('amount', 10000)  # Default amount for testing
            
#             # Update user in database immediately (no verification for testing)
#             success = self.handle_successful_payment(
#                 reference, plan_type, duration_months, user_id, amount
#             )
            
#             if success:
#                 return {'status': 'success', 'message': 'Payment processed and user updated'}, 200
#             else:
#                 return {'status': 'error', 'message': 'Failed to update user'}, 500
            
#         except Exception as e:
#             print(f"Error handling webhook: {e}")
#             return {'status': 'error', 'message': str(e)}, 400
    
#     def handle_successful_payment(self, reference, plan_type, duration_months, user_id, amount):
#         """
#         Handle successful payment - update user account in database
#         """
#         try:
#             # Validate plan_type against database enum values
#             valid_plans = ['free', 'basic', 'premium']
#             if plan_type not in valid_plans:
#                 print(f"Invalid plan type: {plan_type}. Must be one of {valid_plans}")
#                 return False
            
#             # Calculate plan dates
#             start_date = datetime.now()
#             end_date = start_date + timedelta(days=30 * duration_months)
            
#             # Update user plan in database
#             conn = get_db_connection()
#             cursor = conn.cursor()
            
#             query = """
#             UPDATE users 
#             SET plan = %s, 
#                 plan_duration = %s, 
#                 amount_paid = %s, 
#                 plan_start_date = %s, 
#                 plan_end_date = %s 
#             WHERE id = %s
#             """
            
#             cursor.execute(query, (
#                 plan_type, 
#                 duration_months, 
#                 amount,
#                 start_date, 
#                 end_date, 
#                 user_id
#             ))
            
#             conn.commit()
            
#             # Check if update was successful
#             if cursor.rowcount > 0:
#                 print(f"Payment {reference} succeeded for user {user_id}: {plan_type} plan, {duration_months} months, amount: KES {amount/100}")
#                 success = True
#             else:
#                 # If user doesn't exist, try to insert (for testing purposes)
#                 try:
#                     insert_query = """
#                     INSERT INTO users (id, plan, plan_duration, amount_paid, plan_start_date, plan_end_date)
#                     VALUES (%s, %s, %s, %s, %s, %s)
#                     """
#                     cursor.execute(insert_query, (
#                         user_id, plan_type, duration_months, amount, start_date, end_date
#                     ))
#                     conn.commit()
#                     print(f"Created new user {user_id} with payment {reference}: {plan_type} plan, {duration_months} months, amount: KES {amount/100}")
#                     success = True
#                 except Exception as insert_error:
#                     print(f"Failed to create user {user_id}: {insert_error}")
#                     success = False
                
#             cursor.close()
#             conn.close()
            
#             return success
            
#         except mysql.connector.Error as err:
#             print(f"MySQL Error handling successful payment: {err}")
#             return False
#         except Exception as e:
#             print(f"Error handling successful payment: {e}")
#             return False

#     def get_user_plan_info(self, user_id):
#         """
#         Get user's current plan information
#         """
#         try:
#             conn = get_db_connection()
#             cursor = conn.cursor(dictionary=True)
            
#             query = """
#             SELECT plan, plan_duration, amount_paid, plan_start_date, plan_end_date 
#             FROM users WHERE id = %s
#             """
#             cursor.execute(query, (user_id,))
#             user_data = cursor.fetchone()
            
#             cursor.close()
#             conn.close()
            
#             return user_data
            
#         except Exception as e:
#             print(f"Error getting user plan info: {e}")
#             return None

# # ---------------- LOCAL QUESTION GENERATION (No NLTK required) ----------------
# def simple_sentence_tokenize(text):
#     """Simple sentence tokenizer without NLTK"""
#     # Split on common sentence endings
#     sentences = re.split(r'[.!?]+', text)
#     # Filter out empty strings and very short fragments
#     sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
#     return sentences

# def simple_word_tokenize(text):
#     """Simple word tokenizer without NLTK"""
#     return text.split()

# def generate_local_questions(text, num_questions=5):
#     """
#     Generate questions locally without NLTK
#     """
#     questions = []
    
#     # Tokenize into sentences
#     sentences = simple_sentence_tokenize(text)
    
#     # Remove very short sentences
#     sentences = [s for s in sentences if len(s.split()) > 4]
    
#     if not sentences:
#         # Fallback if no good sentences found
#         return [
#             ("What is the main topic of these notes?", "The main topic needs to be identified from your notes."),
#             ("What are the key points mentioned?", "Key points should be extracted from the provided text."),
#             ("How would you summarize this content?", "A summary would capture the essential information."),
#             ("What questions might someone ask about this?", "Questions would test understanding of the material."),
#             ("What further information would be helpful?", "Additional details could provide more context.")
#         ]
    
#     # Generate different types of questions
#     question_types = [
#         _generate_definition_question,
#         _generate_comparison_question,
#         _generate_cause_effect_question,
#         _generate_process_question,
#         _generate_concept_question
#     ]
    
#     # Try to generate different types of questions
#     for i in range(num_questions):
#         if i < len(question_types):
#             try:
#                 q, a = question_types[i](sentences, text)
#                 if q and a:
#                     questions.append((q, a))
#             except:
#                 # If specific question type fails, use a generic one
#                 q, a = _generate_generic_question(sentences, text)
#                 questions.append((q, a))
#         else:
#             # For additional questions beyond our types
#             q, a = _generate_generic_question(sentences, text)
#             questions.append((q, a))
    
#     return questions[:num_questions]  # Ensure we return exactly num_questions

# def _generate_generic_question(sentences, full_text):
#     """Generate a generic question about the text"""
#     if not sentences:
#         return ("What is this text about?", "The text contains information that needs to be analyzed.")
    
#     sentence = random.choice(sentences)
#     words = simple_word_tokenize(sentence)
    
#     # Find longer words that might be important concepts
#     important_words = [word for word in words if len(word) > 5 and word.lower() not in ['because', 'about', 'which', 'should', 'would']]
    
#     if important_words:
#         subject = random.choice(important_words)
#         return (f"What is important about {subject}?", f"{subject} is mentioned in the context: {sentence}")
#     elif words:
#         subject = random.choice(words)
#         return (f"What does '{subject}' refer to?", f"'{subject}' is part of the statement: {sentence}")
#     else:
#         return (f"What is the significance of this statement: '{sentence[:50]}...'?", 
#                 f"This statement is part of the broader context: {full_text[:100]}...")

# def _generate_definition_question(sentences, full_text):
#     """Generate a definition question"""
#     if not sentences:
#         return None, None
        
#     sentence = random.choice(sentences)
#     words = simple_word_tokenize(sentence)
    
#     # Look for nouns that might be concepts to define (longer words)
#     concepts = [word for word in words if len(word) > 5 and word[0].isupper() or len(word) > 7]
    
#     if concepts:
#         concept = random.choice(concepts)
#         return (f"What is the definition of {concept}?", 
#                 f"{concept} is a concept mentioned in: {sentence}")
    
#     return _generate_generic_question(sentences, full_text)

# def _generate_comparison_question(sentences, full_text):
#     """Generate a comparison question"""
#     if len(sentences) < 2:
#         return _generate_generic_question(sentences, full_text)
        
#     sent1, sent2 = random.sample(sentences, 2)
#     words1 = simple_word_tokenize(sent1)
#     words2 = simple_word_tokenize(sent2)
    
#     concepts1 = [word for word in words1 if len(word) > 4]
#     concepts2 = [word for word in words2 if len(word) > 4]
    
#     if concepts1 and concepts2:
#         concept1 = random.choice(concepts1)
#         concept2 = random.choice(concepts2)
#         return (f"How does {concept1} relate to {concept2}?", 
#                 f"Both {concept1} and {concept2} are discussed in the notes. {concept1} appears in: {sent1}. {concept2} appears in: {sent2}")
    
#     return _generate_generic_question(sentences, full_text)

# def _generate_cause_effect_question(sentences, full_text):
#     """Generate a cause and effect question"""
#     cause_words = ['because', 'since', 'due to', 'as a result', 'therefore', 'thus', 'consequently']
    
#     for sentence in sentences:
#         for word in cause_words:
#             if word in sentence.lower():
#                 return (f"What is the relationship described in: '{sentence}'?", 
#                         f"This sentence describes a cause-effect relationship: {sentence}")
    
#     return _generate_generic_question(sentences, full_text)

# def _generate_process_question(sentences, full_text):
#     """Generate a process question"""
#     process_words = ['first', 'next', 'then', 'after', 'before', 'during', 'while', 'until']
    
#     for sentence in sentences:
#         for word in process_words:
#             if word in sentence.lower():
#                 return (f"What is the sequence or process described in: '{sentence}'?", 
#                         f"This sentence describes a process or sequence: {sentence}")
    
#     return _generate_generic_question(sentences, full_text)

# def _generate_concept_question(sentences, full_text):
#     """Generate a conceptual question"""
#     concept_words = ['concept', 'theory', 'principle', 'idea', 'notion', 'framework', 'model']
    
#     for sentence in sentences:
#         for word in concept_words:
#             if word in sentence.lower():
#                 return (f"What is the main concept in: '{sentence}'?", 
#                         f"This sentence introduces a key concept: {sentence}")
    
#     return _generate_generic_question(sentences, full_text)

# # ---------------- AUTH ----------------
# @app.route('/')
# def home():
#     if "user_id" in session:
#         return redirect(url_for('dashboard'))
#     return render_template("index.html")

# @app.route('/signup', methods=['GET','POST'])
# def signup():
#     if request.method == "POST":
#         name = request.form['name']
#         email = request.form['email']
#         password = hashlib.sha256(request.form['password'].encode()).hexdigest()

#         conn = get_db_connection()
#         if conn is None:
#             flash("Database error.", "danger")
#             return render_template("signup.html")

#         cur = conn.cursor()
#         try:
#             cur.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name,email,password))
#             conn.commit()
#             flash("Account created! Please login.","success")
#             return redirect(url_for('login'))
#         except mysql.connector.Error as err:
#             flash("Email already exists.","danger")
#             logger.error(err)
#         finally:
#             conn.close()
#     return render_template("signup.html")

# @app.route('/login', methods=['GET','POST'])
# def login():
#     if request.method == "POST":
#         email = request.form['email']
#         password = hashlib.sha256(request.form['password'].encode()).hexdigest()

#         conn = get_db_connection()
#         if conn is None:
#             flash("Database error.", "danger")
#             return render_template("login.html")

#         cur = conn.cursor(dictionary=True)
#         cur.execute("SELECT * FROM users WHERE email=%s AND password=%s",(email,password))
#         user = cur.fetchone()
#         conn.close()

#         if user:
#             session["user_id"] = user['id']
#             session["name"] = user['name']
#             session["plan"] = user.get('plan', 'free')
#             return redirect(url_for("dashboard"))
#         else:
#             flash("Invalid credentials.","danger")
#     return render_template("login.html")

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('home'))

# # ---------------- DASHBOARD ----------------
# @app.route('/dashboard')
# def dashboard():
#     if "user_id" not in session: 
#         return redirect(url_for('login'))
    
#     conn = get_db_connection()
#     cards = []
#     total_cards = 0
#     mastered_cards = 0
    
#     if conn:
#         cur = conn.cursor(dictionary=True)
#         # Get user's flashcards
#         cur.execute("SELECT * FROM flashcards WHERE user_id=%s ORDER BY created_at DESC", (session['user_id'],))
#         cards = cur.fetchall()
        
#         # Get total count of flashcards for this user
#         cur.execute("SELECT COUNT(*) as total FROM flashcards WHERE user_id=%s", (session['user_id'],))
#         total_result = cur.fetchone()
#         total_cards = total_result['total'] if total_result else 0
        
#         # Get mastered cards count (if mastered column exists)
#         try:
#             cur.execute("SELECT COUNT(*) as mastered FROM flashcards WHERE user_id=%s AND mastered=1", (session['user_id'],))
#             mastered_result = cur.fetchone()
#             mastered_cards = mastered_result['mastered'] if mastered_result else 0
#         except:
#             mastered_cards = 0
            
#         # Get user's current plan from database
#         cur.execute("SELECT plan FROM users WHERE id=%s", (session['user_id'],))
#         user_result = cur.fetchone()
#         user_plan = user_result['plan'] if user_result else 'free'
#         session["plan"] = user_plan  # Update session with current plan
        
#         conn.close()
    
#     return render_template("dashboard.html", 
#                          flashcards=cards, 
#                          name=session.get("name", "User"), 
#                          plan=session.get("plan", "free"),
#                          total_cards=total_cards,
#                          mastered_cards=mastered_cards)

# @app.route('/premium')
# def premium():
#     if "user_id" not in session: 
#         return redirect(url_for('login'))
#     return render_template("premium.html")

# # ---------------- PAYMENT ROUTES ----------------
# @app.route('/paystack-webhook', methods=['POST'])
# def paystack_webhook():
#     processor = PaymentProcessor()
#     result, status_code = processor.handle_webhook(request.data)
#     return jsonify(result), status_code

# @app.route('/verify-payment/<reference>', methods=['GET'])
# def verify_payment(reference):
#     processor = PaymentProcessor()
#     result = processor.verify_transaction(reference)
    
#     if result:
#         return jsonify(result)
#     else:
#         return jsonify({'status': 'error', 'message': 'Failed to verify transaction'}), 400

# @app.route('/user/<int:user_id>/plan', methods=['GET'])
# def get_user_plan(user_id):
#     processor = PaymentProcessor()
#     user_data = processor.get_user_plan_info(user_id)
    
#     if user_data:
#         return jsonify({
#             'status': 'success',
#             'data': user_data
#         })
#     else:
#         return jsonify({
#             'status': 'error',
#             'message': 'User not found or error retrieving data'
#         }), 404

# # New endpoint for testing - simulate payment without webhook
# @app.route('/simulate-payment', methods=['POST'])
# def simulate_payment():
#     if "user_id" not in session: 
#         return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
        
#     processor = PaymentProcessor()
    
#     # Get data from request or use defaults
#     data = request.get_json() or {}
#     reference = data.get('reference', 'test_ref_' + datetime.now().strftime('%Y%m%d%H%M%S'))
#     plan_type = data.get('plan_type', 'premium')
#     duration_months = int(data.get('duration_months', 1))
#     user_id = session['user_id']  # Use logged in user ID
#     amount = data.get('amount', 10000)  # Amount in Kobo (10000 = 100 KES)
    
#     # Process payment immediately
#     success = processor.handle_successful_payment(
#         reference, plan_type, duration_months, user_id, amount
#     )
    
#     if success:
#         # Update session with new plan
#         session["plan"] = plan_type
#         return jsonify({
#             'status': 'success', 
#             'message': f'Payment simulated successfully for user {user_id}',
#             'reference': reference,
#             'plan': plan_type
#         }), 200
#     else:
#         return jsonify({
#             'status': 'error', 
#             'message': 'Failed to simulate payment'
#         }), 500

# # ---------------- GENERATE FLASHCARDS ----------------
# @app.route('/generate', methods=['POST'])
# def generate():
#     if "user_id" not in session: 
#         return jsonify({"success": False, "error": "Not authenticated"}), 401
    
#     # Check if user is free and has reached the limit
#     user_plan = session.get("plan", "free")
#     if user_plan == "free":
#         conn = get_db_connection()
#         if conn:
#             cur = conn.cursor(dictionary=True)
#             cur.execute("SELECT COUNT(*) as total FROM flashcards WHERE user_id=%s",(session['user_id'],))
#             total_result = cur.fetchone()
#             total_cards = total_result['total'] if total_result else 0
#             conn.close()
            
#             if total_cards >= 10:
#                 return jsonify({
#                     "success": False,
#                     "error": "limit_reached",
#                     "message": "❌ Free plan limit reached! You've created 10 flashcards. Upgrade to Premium for unlimited access and advanced features."
#                 }), 403
    
#     notes = request.form['notes']
#     if not notes or len(notes.strip()) < 10:
#         return jsonify({"success": False, "error": "Please provide meaningful notes (at least 10 characters)"}), 400
        
#     logger.info(f"Generating flashcards locally for user {session['user_id']}")
    
#     # Use local question generation only
#     flashcards = generate_local_questions(notes, 5)

#     # Check free user limit again before saving
#     user_plan = session.get("plan", "free")
#     if user_plan == "free":
#         conn = get_db_connection()
#         if conn:
#             cur = conn.cursor(dictionary=True)
#             cur.execute("SELECT COUNT(*) as total FROM flashcards WHERE user_id=%s",(session['user_id'],))
#             total_result = cur.fetchone()
#             total_cards = total_result['total'] if total_result else 0
#             conn.close()
            
#             # Calculate how many new cards we can actually save
#             available_slots = 10 - total_cards
#             if available_slots <= 0:
#                 return jsonify({
#                     "success": False,
#                     "error": "limit_reached",
#                     "message": "❌ Free plan limit reached! You've created 10 flashcards. Upgrade to Premium for unlimited access and advanced features."
#                 }), 403
                
#             # Limit the number of flashcards to available slots
#             flashcards = flashcards[:available_slots]

#     # Save to DB
#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"success": False, "error": "Database connection error"}), 500
        
#     cur = conn.cursor()
#     cards_saved = 0
#     for q, a in flashcards:
#         try:
#             cur.execute("INSERT INTO flashcards (user_id, question, answer) VALUES (%s,%s,%s)", 
#                         (session['user_id'], q, a))
#             cards_saved += 1
#         except mysql.connector.Error as err:
#             logger.error(f"Error saving flashcard: {err}")
    
#     conn.commit()
#     conn.close()

#     # Check if user reached the limit after saving
#     user_plan = session.get("plan", "free")
#     limit_reached = False
#     if user_plan == "free":
#         new_total = total_cards + cards_saved
#         if new_total >= 10:
#             limit_reached = True

#     return jsonify({
#         "success": True,
#         "message": f"Generated {cards_saved} flashcards successfully!" + 
#                   (" ❌ You've reached the free limit of 10 flashcards. Upgrade to Premium for unlimited access." if limit_reached else ""),
#         "flashcards": [{"question": q, "answer": a} for q, a in flashcards[:cards_saved]],
#         "total_cards": total_cards + cards_saved if 'total_cards' in locals() else cards_saved,
#         "limit_reached": limit_reached
#     })

# # ---------------- API: GET FLASHCARDS ----------------
# @app.route('/api/flashcards')
# def api_flashcards():
#     if "user_id" not in session: 
#         return jsonify({"error": "Not authenticated"}), 401
#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"error": "Database connection failed"}), 500
#     cur = conn.cursor(dictionary=True)
#     cur.execute("SELECT * FROM flashcards WHERE user_id=%s ORDER BY created_at DESC",(session['user_id'],))
#     cards = cur.fetchall()
#     conn.close()
#     return jsonify(cards)

# # ---------------- API: GET USER STATS ----------------
# @app.route('/api/user/stats')
# def api_user_stats():
#     if "user_id" not in session: 
#         return jsonify({"error": "Not authenticated"}), 401
        
#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"error": "Database connection failed"}), 500
        
#     cur = conn.cursor(dictionary=True)
    
#     # Get total flashcards count
#     cur.execute("SELECT COUNT(*) as total FROM flashcards WHERE user_id=%s",(session['user_id'],))
#     total_result = cur.fetchone()
#     total_cards = total_result['total'] if total_result else 0
    
#     # Get mastered cards count (assuming a 'mastered' column exists)
#     try:
#         cur.execute("SELECT COUNT(*) as mastered FROM flashcards WHERE user_id=%s AND mastered=1",(session['user_id'],))
#         mastered_result = cur.fetchone()
#         mastered_cards = mastered_result['mastered'] if mastered_result else 0
#     except:
#         mastered_cards = 0
    
#     conn.close()
    
#     return jsonify({
#         "total_cards": total_cards,
#         "mastered_cards": mastered_cards,
#         "plan": session.get("plan", "free"),
#         "max_cards": 10 if session.get("plan", "free") == "free" else float('inf')
#     })

# if __name__ == "__main__":
#     app.run(debug=True, port=5001)
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector, hashlib
import re, logging, random, string
from datetime import datetime, timedelta
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Paystack configuration (only secret key needed for verification)
PAYSTACK_SECRET_KEY = "sk_test_34d568ac6ea779fe94bafe563e481b7c163dfcb0"

# Database configuration
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="hackerthone_db"
        )
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection failed: {err}")
        return None

# ---------------- PAYMENT PROCESSOR CLASS ----------------
class PaymentProcessor:
    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
    
    def verify_transaction(self, reference):
        """
        Verify a Paystack transaction - SIMULATED FOR TESTING
        """
        try:
            # For testing, simulate a successful response
            simulated_response = {
                'status': True,
                'message': 'Verification successful',
                'data': {
                    'status': 'success',
                    'reference': reference,
                    'amount': 10000,  # Example amount in Kobo
                    'currency': 'KES',
                    'metadata': {
                        'plan_type': 'premium',
                        'duration_months': 1,
                        'user_id': session.get('user_id', 1)
                    }
                }
            }
            return simulated_response
                
        except Exception as e:
            print(f"Error verifying transaction: {e}")
            return None
    
    def handle_webhook(self, payload):
        """
        Handle webhook events from Paystack - MODIFIED FOR INSTANT PROCESSING
        """
        try:
            # For testing, accept any payload and process immediately
            if isinstance(payload, bytes):
                payload = payload.decode('utf-8')
            
            # Try to parse as JSON, but if it fails, create a simulated event
            try:
                event = json.loads(payload)
            except json.JSONDecodeError:
                # Create a simulated successful payment event for testing
                event = {
                    'event': 'charge.success',
                    'data': {
                        'reference': 'test_ref_' + datetime.now().strftime('%Y%m%d%H%M%S'),
                        'amount': 10000,
                        'metadata': {
                            'plan_type': 'premium',
                            'duration_months': 1,
                            'user_id': session.get('user_id', 1)
                        }
                    }
                }
            
            # Process any event as successful for testing
            data = event.get('data', {})
            reference = data.get('reference', 'test_ref_' + datetime.now().strftime('%Y%m%d%H%M%S'))
            
            # Extract metadata with defaults for testing
            metadata = data.get('metadata', {})
            plan_type = metadata.get('plan_type', 'premium')
            duration_months = int(metadata.get('duration_months', 1))
            
            # Get user_id from metadata or session
            user_id = metadata.get('user_id')
            if user_id is None:
                user_id = session.get('user_id', 1)
            user_id = int(user_id)
            
            amount = data.get('amount', 10000)
            
            # Update user in database immediately (no verification for testing)
            success = self.handle_successful_payment(
                reference, plan_type, duration_months, user_id, amount
            )
            
            if success:
                return {'status': 'success', 'message': 'Payment processed and user updated'}, 200
            else:
                return {'status': 'error', 'message': 'Failed to update user'}, 500
            
        except Exception as e:
            print(f"Error handling webhook: {e}")
            return {'status': 'error', 'message': str(e)}, 400
    
    def handle_successful_payment(self, reference, plan_type, duration_months, user_id, amount):
        """
        Handle successful payment - update user account in database
        """
        try:
            # Validate plan_type against database enum values
            valid_plans = ['free', 'basic', 'premium']
            if plan_type not in valid_plans:
                print(f"Invalid plan type: {plan_type}. Must be one of {valid_plans}")
                return False
            
            # Convert amount from kobo to actual currency value (divide by 100)
            amount_decimal = float(amount) / 100
            
            # Calculate plan dates
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30 * duration_months)
            
            # Update user plan in database
            conn = get_db_connection()
            if conn is None:
                print("Database connection failed")
                return False
                
            cursor = conn.cursor()
            
            # First check if user exists
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            user_exists = cursor.fetchone()
            
            if user_exists:
                # Update existing user
                query = """
                UPDATE users 
                SET plan = %s, 
                    plan_duration = %s, 
                    amount_paid = %s, 
                    plan_start_date = %s, 
                    plan_end_date = %s,
                    updated_at = NOW()
                WHERE id = %s
                """
                
                cursor.execute(query, (
                    plan_type, 
                    duration_months, 
                    amount_decimal,  # Use the converted decimal value
                    start_date, 
                    end_date, 
                    user_id
                ))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    print(f"Payment {reference} succeeded for user {user_id}: {plan_type} plan, {duration_months} months, amount: {amount_decimal}")
                    success = True
                else:
                    print(f"No rows affected for user {user_id}")
                    success = False
            else:
                print(f"User {user_id} does not exist in database")
                success = False
                
            cursor.close()
            conn.close()
            
            return success
            
        except mysql.connector.Error as err:
            print(f"MySQL Error handling successful payment: {err}")
            return False
        except Exception as e:
            print(f"Error handling successful payment: {e}")
            return False

    def get_user_plan_info(self, user_id):
        """
        Get user's current plan information
        """
        try:
            conn = get_db_connection()
            if conn is None:
                return None
                
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT id, name, email, plan, plan_duration, amount_paid, plan_start_date, plan_end_date 
            FROM users WHERE id = %s
            """
            cursor.execute(query, (user_id,))
            user_data = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return user_data
            
        except Exception as e:
            print(f"Error getting user plan info: {e}")
            return None

# ---------------- LOCAL QUESTION GENERATION (No NLTK required) ----------------
def simple_sentence_tokenize(text):
    """Simple sentence tokenizer without NLTK"""
    # Split on common sentence endings
    sentences = re.split(r'[.!?]+', text)
    # Filter out empty strings and very short fragments
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    return sentences

def simple_word_tokenize(text):
    """Simple word tokenizer without NLTK"""
    return text.split()

def generate_local_questions(text, num_questions=5):
    """
    Generate questions locally without NLTK
    """
    questions = []
    
    # Tokenize into sentences
    sentences = simple_sentence_tokenize(text)
    
    # Remove very short sentences
    sentences = [s for s in sentences if len(s.split()) > 4]
    
    if not sentences:
        # Fallback if no good sentences found
        return [
            ("What is the main topic of these notes?", "The main topic needs to be identified from your notes."),
            ("What are the key points mentioned?", "Key points should be extracted from the provided text."),
            ("How would you summarize this content?", "A summary would capture the essential information."),
            ("What questions might someone ask about this?", "Questions would test understanding of the material."),
            ("What further information would be helpful?", "Additional details could provide more context.")
        ]
    
    # Generate different types of questions
    question_types = [
        _generate_definition_question,
        _generate_comparison_question,
        _generate_cause_effect_question,
        _generate_process_question,
        _generate_concept_question
    ]
    
    # Try to generate different types of questions
    for i in range(num_questions):
        if i < len(question_types):
            try:
                q, a = question_types[i](sentences, text)
                if q and a:
                    questions.append((q, a))
            except:
                # If specific question type fails, use a generic one
                q, a = _generate_generic_question(sentences, text)
                questions.append((q, a))
        else:
            # For additional questions beyond our types
            q, a = _generate_generic_question(sentences, text)
            questions.append((q, a))
    
    return questions[:num_questions]  # Ensure we return exactly num_questions

def _generate_generic_question(sentences, full_text):
    """Generate a generic question about the text"""
    if not sentences:
        return ("What is this text about?", "The text contains information that needs to be analyzed.")
    
    sentence = random.choice(sentences)
    words = simple_word_tokenize(sentence)
    
    # Find longer words that might be important concepts
    important_words = [word for word in words if len(word) > 5 and word.lower() not in ['because', 'about', 'which', 'should', 'would']]
    
    if important_words:
        subject = random.choice(important_words)
        return (f"What is important about {subject}?", f"{subject} is mentioned in the context: {sentence}")
    elif words:
        subject = random.choice(words)
        return (f"What does '{subject}' refer to?", f"'{subject}' is part of the statement: {sentence}")
    else:
        return (f"What is the significance of this statement: '{sentence[:50]}...'?", 
                f"This statement is part of the broader context: {full_text[:100]}...")

def _generate_definition_question(sentences, full_text):
    """Generate a definition question"""
    if not sentences:
        return None, None
        
    sentence = random.choice(sentences)
    words = simple_word_tokenize(sentence)
    
    # Look for nouns that might be concepts to define (longer words)
    concepts = [word for word in words if len(word) > 5 and word[0].isupper() or len(word) > 7]
    
    if concepts:
        concept = random.choice(concepts)
        return (f"What is the definition of {concept}?", 
                f"{concept} is a concept mentioned in: {sentence}")
    
    return _generate_generic_question(sentences, full_text)

def _generate_comparison_question(sentences, full_text):
    """Generate a comparison question"""
    if len(sentences) < 2:
        return _generate_generic_question(sentences, full_text)
        
    sent1, sent2 = random.sample(sentences, 2)
    words1 = simple_word_tokenize(sent1)
    words2 = simple_word_tokenize(sent2)
    
    concepts1 = [word for word in words1 if len(word) > 4]
    concepts2 = [word for word in words2 if len(word) > 4]
    
    if concepts1 and concepts2:
        concept1 = random.choice(concepts1)
        concept2 = random.choice(concepts2)
        return (f"How does {concept1} relate to {concept2}?", 
                f"Both {concept1} and {concept2} are discussed in the notes. {concept1} appears in: {sent1}. {concept2} appears in: {sent2}")
    
    return _generate_generic_question(sentences, full_text)

def _generate_cause_effect_question(sentences, full_text):
    """Generate a cause and effect question"""
    cause_words = ['because', 'since', 'due to', 'as a result', 'therefore', 'thus', 'consequently']
    
    for sentence in sentences:
        for word in cause_words:
            if word in sentence.lower():
                return (f"What is the relationship described in: '{sentence}'?", 
                        f"This sentence describes a cause-effect relationship: {sentence}")
    
    return _generate_generic_question(sentences, full_text)

def _generate_process_question(sentences, full_text):
    """Generate a process question"""
    process_words = ['first', 'next', 'then', 'after', 'before', 'during', 'while', 'until']
    
    for sentence in sentences:
        for word in process_words:
            if word in sentence.lower():
                return (f"What is the sequence or process described in: '{sentence}'?", 
                        f"This sentence describes a process or sequence: {sentence}")
    
    return _generate_generic_question(sentences, full_text)

def _generate_concept_question(sentences, full_text):
    """Generate a conceptual question"""
    concept_words = ['concept', 'theory', 'principle', 'idea', 'notion', 'framework', 'model']
    
    for sentence in sentences:
        for word in concept_words:
            if word in sentence.lower():
                return (f"What is the main concept in: '{sentence}'?", 
                        f"This sentence introduces a key concept: {sentence}")
    
    return _generate_generic_question(sentences, full_text)

# ---------------- AUTH ----------------
@app.route('/')
def home():
    if "user_id" in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        conn = get_db_connection()
        if conn is None:
            flash("Database error.", "danger")
            return render_template("signup.html")

        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name,email,password))
            conn.commit()
            flash("Account created! Please login.","success")
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash("Email already exists.","danger")
            logger.error(err)
        finally:
            conn.close()
    return render_template("signup.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        conn = get_db_connection()
        if conn is None:
            flash("Database error.", "danger")
            return render_template("login.html")

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s",(email,password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user['id']
            session["name"] = user['name']
            session["plan"] = user.get('plan', 'free')
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials.","danger")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if "user_id" not in session: 
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cards = []
    total_cards = 0
    mastered_cards = 0
    
    if conn:
        cur = conn.cursor(dictionary=True)
        # Get user's flashcards
        cur.execute("SELECT * FROM flashcards WHERE user_id=%s ORDER BY created_at DESC", (session['user_id'],))
        cards = cur.fetchall()
        
        # Get total count of flashcards for this user
        cur.execute("SELECT COUNT(*) as total FROM flashcards WHERE user_id=%s", (session['user_id'],))
        total_result = cur.fetchone()
        total_cards = total_result['total'] if total_result else 0
        
        # Get mastered cards count (if mastered column exists)
        try:
            cur.execute("SELECT COUNT(*) as mastered FROM flashcards WHERE user_id=%s AND mastered=1", (session['user_id'],))
            mastered_result = cur.fetchone()
            mastered_cards = mastered_result['mastered'] if mastered_result else 0
        except:
            mastered_cards = 0
            
        # Get user's current plan from database
        cur.execute("SELECT plan, plan_duration, amount_paid, plan_start_date, plan_end_date FROM users WHERE id=%s", (session['user_id'],))
        user_result = cur.fetchone()
        if user_result:
            user_plan = user_result['plan'] if user_result['plan'] else 'free'
            session["plan"] = user_plan  # Update session with current plan
            session["plan_details"] = user_result  # Store all plan details
        
        conn.close()
    
    return render_template("dashboard.html", 
                         flashcards=cards, 
                         name=session.get("name", "User"), 
                         plan=session.get("plan", "free"),
                         total_cards=total_cards,
                         mastered_cards=mastered_cards)

@app.route('/premium')
def premium():
    if "user_id" not in session: 
        return redirect(url_for('login'))
    
    # Get current user plan details
    processor = PaymentProcessor()
    user_data = processor.get_user_plan_info(session['user_id'])
    
    return render_template("premium.html", user_data=user_data)

# ---------------- PAYMENT ROUTES ----------------
@app.route('/paystack-webhook', methods=['POST'])
def paystack_webhook():
    processor = PaymentProcessor()
    result, status_code = processor.handle_webhook(request.data)
    return jsonify(result), status_code

@app.route('/verify-payment/<reference>', methods=['GET'])
def verify_payment(reference):
    processor = PaymentProcessor()
    result = processor.verify_transaction(reference)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'status': 'error', 'message': 'Failed to verify transaction'}), 400

@app.route('/user/<int:user_id>/plan', methods=['GET'])
def get_user_plan(user_id):
    processor = PaymentProcessor()
    user_data = processor.get_user_plan_info(user_id)
    
    if user_data:
        return jsonify({
            'status': 'success',
            'data': user_data
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'User not found or error retrieving data'
        }), 404

# New endpoint for testing - simulate payment without webhook
@app.route('/simulate-payment', methods=['POST'])
def simulate_payment():
    if "user_id" not in session: 
        return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
        
    processor = PaymentProcessor()
    
    # Get data from request or use defaults
    data = request.get_json() or {}
    reference = data.get('reference', 'test_ref_' + datetime.now().strftime('%Y%m%d%H%M%S'))
    plan_type = data.get('plan_type', 'premium')
    duration_months = int(data.get('duration_months', 1))
    user_id = session['user_id']  # Use logged in user ID
    amount = data.get('amount', 10000)  # Amount in Kobo (10000 = 100 KES)
    
    # Process payment immediately
    success = processor.handle_successful_payment(
        reference, plan_type, duration_months, user_id, amount
    )
    
    if success:
        # Update session with new plan
        session["plan"] = plan_type
        
        # Refresh user data from database
        user_data = processor.get_user_plan_info(user_id)
        if user_data:
            session["plan_details"] = user_data
        
        return jsonify({
            'status': 'success', 
            'message': f'Payment simulated successfully for user {user_id}',
            'reference': reference,
            'plan': plan_type
        }), 200
    else:
        return jsonify({
            'status': 'error', 
            'message': 'Failed to simulate payment'
        }), 500

# ---------------- DEBUG ROUTES ----------------
@app.route('/debug/user/<int:user_id>')
def debug_user(user_id):
    """Debug endpoint to check user data"""
    if "user_id" not in session: 
        return jsonify({"error": "Not authenticated"}), 401
        
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    conn.close()
    
    return jsonify(user or {"error": "User not found"})

@app.route('/debug/update-plan', methods=['POST'])
def debug_update_plan():
    """Debug endpoint to manually update user plan"""
    if "user_id" not in session: 
        return jsonify({"error": "Not authenticated"}), 401
        
    data = request.get_json()
    plan_type = data.get('plan_type', 'premium')
    duration_months = data.get('duration_months', 1)
    amount = data.get('amount', 10000)
    
    processor = PaymentProcessor()
    success = processor.handle_successful_payment(
        'debug_ref_' + datetime.now().strftime('%Y%m%d%H%M%S'),
        plan_type,
        duration_months,
        session['user_id'],
        amount
    )
    
    if success:
        session["plan"] = plan_type
        return jsonify({"status": "success", "message": "Plan updated"})
    else:
        return jsonify({"status": "error", "message": "Failed to update plan"}), 500

# ---------------- GENERATE FLASHCARDS ----------------
@app.route('/generate', methods=['POST'])
def generate():
    if "user_id" not in session: 
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    # Check if user is free and has reached the limit
    user_plan = session.get("plan", "free")
    if user_plan == "free":
        conn = get_db_connection()
        if conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT COUNT(*) as total FROM flashcards WHERE user_id=%s",(session['user_id'],))
            total_result = cur.fetchone()
            total_cards = total_result['total'] if total_result else 0
            conn.close()
            
            if total_cards >= 10:
                return jsonify({
                    "success": False,
                    "error": "limit_reached",
                    "message": "❌ Free plan limit reached! You've created 10 flashcards. Upgrade to Premium for unlimited access and advanced features."
                }), 403
    
    notes = request.form['notes']
    if not notes or len(notes.strip()) < 10:
        return jsonify({"success": False, "error": "Please provide meaningful notes (at least 10 characters)"}), 400
        
    logger.info(f"Generating flashcards locally for user {session['user_id']}")
    
    # Use local question generation only
    flashcards = generate_local_questions(notes, 5)

    # Check free user limit again before saving
    user_plan = session.get("plan", "free")
    if user_plan == "free":
        conn = get_db_connection()
        if conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT COUNT(*) as total FROM flashcards WHERE user_id=%s",(session['user_id'],))
            total_result = cur.fetchone()
            total_cards = total_result['total'] if total_result else 0
            conn.close()
            
            # Calculate how many new cards we can actually save
            available_slots = 10 - total_cards
            if available_slots <= 0:
                return jsonify({
                    "success": False,
                    "error": "limit_reached",
                    "message": "❌ Free plan limit reached! You've created 10 flashcards. Upgrade to Premium for unlimited access and advanced features."
                }), 403
                
            # Limit the number of flashcards to available slots
            flashcards = flashcards[:available_slots]

    # Save to DB
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database connection error"}), 500
        
    cur = conn.cursor()
    cards_saved = 0
    for q, a in flashcards:
        try:
            cur.execute("INSERT INTO flashcards (user_id, question, answer) VALUES (%s,%s,%s)", 
                        (session['user_id'], q, a))
            cards_saved += 1
        except mysql.connector.Error as err:
            logger.error(f"Error saving flashcard: {err}")
    
    conn.commit()
    conn.close()

    # Check if user reached the limit after saving
    user_plan = session.get("plan", "free")
    limit_reached = False
    if user_plan == "free":
        new_total = total_cards + cards_saved
        if new_total >= 10:
            limit_reached = True

    return jsonify({
        "success": True,
        "message": f"Generated {cards_saved} flashcards successfully!" + 
                  (" ❌ You've reached the free limit of 10 flashcards. Upgrade to Premium for unlimited access." if limit_reached else ""),
        "flashcards": [{"question": q, "answer": a} for q, a in flashcards[:cards_saved]],
        "total_cards": total_cards + cards_saved if 'total_cards' in locals() else cards_saved,
        "limit_reached": limit_reached
    })

# ---------------- API: GET FLASHCARDS ----------------
@app.route('/api/flashcards')
def api_flashcards():
    if "user_id" not in session: 
        return jsonify({"error": "Not authenticated"}), 401
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM flashcards WHERE user_id=%s ORDER BY created_at DESC",(session['user_id'],))
    cards = cur.fetchall()
    conn.close()
    return jsonify(cards)

# ---------------- API: GET USER STATS ----------------
@app.route('/api/user/stats')
def api_user_stats():
    if "user_id" not in session: 
        return jsonify({"error": "Not authenticated"}), 401
        
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    cur = conn.cursor(dictionary=True)
    
    # Get total flashcards count
    cur.execute("SELECT COUNT(*) as total FROM flashcards WHERE user_id=%s",(session['user_id'],))
    total_result = cur.fetchone()
    total_cards = total_result['total'] if total_result else 0
    
    # Get mastered cards count (assuming a 'mastered' column exists)
    try:
        cur.execute("SELECT COUNT(*) as mastered FROM flashcards WHERE user_id=%s AND mastered=1",(session['user_id'],))
        mastered_result = cur.fetchone()
        mastered_cards = mastered_result['mastered'] if mastered_result else 0
    except:
        mastered_cards = 0
    
    conn.close()
    
    return jsonify({
        "total_cards": total_cards,
        "mastered_cards": mastered_cards,
        "plan": session.get("plan", "free"),
        "max_cards": 10 if session.get("plan", "free") == "free" else float('inf')
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)