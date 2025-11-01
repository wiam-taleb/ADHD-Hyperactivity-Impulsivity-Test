from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from ADHD_HI import ADHDDiagnosis

app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return render_template('index.html')
    
if _name_ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

QUESTIONS_AR = [
    "هل تشعر بالتململ أو تجد صعوبة في البقاء هادئاً؟",
    "هل تفرك يديك أو قدميك أو تنقر بالأشياء أثناء الجلوس؟",
    "هل غالبًا ما تنهض من مقعدك عندما يتوقع منك البقاء جالساً؟",
    "هل تجد صعوبة في العمل أو اللعب في بيئة هادئة؟",
    "هل تتحدث كثيراً أو تقاطع الآخرين بكثرة؟",
    "هل تجري أو تتحرك بشكل مفرط في أماكن غير مناسبة؟",
    "هل تبدأ مهام متعددة ونادراً ما تكملها؟",
    "هل تفقد التركيز بسهولة حتى أثناء الأنشطة المهمة أو المثيرة للاهتمام؟",
    "هل تتصرف بناءً على عواطفك بسرعة (مثل الغضب أو الحماس دون تفكير)؟",
    "هل تجد صعوبة في انتظار دورك في الطوابير أو المحادثات؟",
    "هل تندفع بالإجابة أو تقول أشياء دون التفكير في مدى ملاءمتها؟",
    "هل تتخذ قرارات مهمة أو تخاطر بشكل كبير دون التفكير في العواقب طويلة الأمد؟"
]


def get_severity_translation(severity_en, lang):
    """ترجمة مستوى الشدة من الإنجليزية للعربية"""
    if lang == 'ar':
        translations = {
            "Very mild symptoms or no initial diagnosis": "أعراض خفيفة جداً أو لا يوجد تشخيص أولي",
            "Mild Presentation": "شدة بسيطة ",
            "Moderate Presentation - Formal assessment recommended": "شدة متوسطة - ينصح بالتقييم الرسمي",
            "Severe Presentation - Urgent need for formal assessment": "شدة متقدمة/شديدة  - ضرورة قصوى للتقييم الرسمي",
            "Error in score calculation": "خطأ في حساب النقاط"
        }
        return translations.get(severity_en, severity_en)
    return severity_en


@app.route('/')
def index():
    """عرض الصفحة الرئيسية"""
    return render_template('index.html')


@app.route('/api/questions', methods=['GET'])
def get_questions():
    """إرجاع الأسئلة من نظام الخبراء ADHD_HI"""
    lang = request.args.get('lang', 'ar')

    
    engine = ADHDDiagnosis()

   
    questions_en = [engine.rules_text[i] for i in range(1, 13)]


    questions = QUESTIONS_AR if lang == 'ar' else questions_en

    return jsonify({
        'questions': questions,
        'success': True
    })


@app.route('/api/calculate', methods=['POST'])
def calculate_result():
    """حساب النتيجة النهائية باستخدام نظام الخبراء ADHD_HI"""
    try:
        data = request.json
        answers = data.get('answers', [])
        lang = data.get('lang', 'ar')

        engine = ADHDDiagnosis()
        engine.reset()

  
        total_score = 0
        for i, answer in enumerate(answers):
            rule_number = i + 1
            if answer and rule_number in engine.rules_data:
                total_score += engine.rules_data[rule_number]

     
        score = total_score
        if score <= 6:
            severity = "Very mild symptoms or no initial diagnosis"
        elif 7 <= score <= 12:
            severity = "Mild Presentation"
        elif 13 <= score <= 18:
            severity = "Moderate Presentation - Formal assessment recommended"
        elif 19 <= score <= 24:
            severity = "Severe Presentation - Urgent need for formal assessment"
        else:
            severity = "Error in score calculation"

        severity_translated = get_severity_translation(severity, lang)

       
        print("\n==============================")
        print("✅ Initial Diagnosis Results for Hyperactive-Impulsive Pattern")
        print("==============================")
        print(f"Total Score: {score} out of 24 points.")
        print(f"Initial Severity Classification: {severity}")
        print("==============================")

        return jsonify({
            'score': total_score,
            'max_score': 24,
            'severity': severity_translated,
            'success': True
        })

    except Exception as e:
        print(f"❌ Error calculating result: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500







