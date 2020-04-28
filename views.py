from flask import Flask, render_template, request, Markup

app = Flask(__name__)

questions = {
    # No : [ Question, [(code, reponse), ( , )...], QCU?QCM]
    1 : ["Quelle est la couleur du cheval blanc d'henri 4 ?", 
        [('A', "Réponse A"), ('B', "Réponse B"), ('C', "Réponse C")],
        True ],
    2 : ["Quelle est votre matiere préférée ?",
        [('A', "Les mathématiques"), ('B', "La fizik"), ('C', "La SVT"), ('D', "La filo")],
        False],
    3 : ["Les maths C mieux", 
        [('V', "VRAI"), ('F', "FAUX")],
        True]
}

reponses = dict()

q_en_cours = 0

def ajoute_reponse(q, r):
    """Ajoute une reponse r à la question q"""
    if not q in reponses:
        reponses[q] = dict()
    if r in reponses[q]:
        reponses[q][r] += 1
    else:
        reponses[q][r] = 1

@app.route('/index.html', methods=["GET"])
def index():
    try:
        n_quest_form = request.args
        n_quest = int(n_quest_form["q"])
    except:
        n_quest = 0
    if q_en_cours == 0 or q_en_cours == n_quest:
        return render_template('index.html')
    else:
        return render_template('redirect.html')

#
# Choix nouvelle question
#

@app.route('/admin.html')
def admin():
    listquest = '<input type="radio" name="n_quest" value="0" id="rep0" /> <label for="rep0">Page d\'attente</label><br />'
    liste_no_questions = list(questions.keys())
    liste_no_questions.sort()
    for q in liste_no_questions:
        if q == q_en_cours :
            listquest += f'<input type="radio" name="n_quest" value="{q}" id="rep{q}" checked/> <label for="rep{q}">{questions[q][0]}</label><br />'
        else:
            listquest += f'<input type="radio" name="n_quest" value="{q}" id="rep{q}" /> <label for="rep{q}">{questions[q][0]}</label><br />'
    return render_template('admin.html', liste_questions=Markup(listquest))

@app.route('/choixrep.html', methods=["POST"])
def choixrep():
    global q_en_cours
    reponse = request.form
    q_en_cours = int(reponse["n_quest"])
    return render_template('choixrep.html')

#
# formulaire questions
#

@app.route('/formulaire.html')
def formulaire():
    quizzstr = ''
    for q in questions[q_en_cours][1]:
        if questions[q_en_cours][2]:
            quizzstr += f'<input type="radio" name="repcu" value="{q[0]}" id="rep{q[0]}" /> <label for="rep{q[0]}">{q[1]}</label><br />'
        else:
            quizzstr += f'<input type="checkbox" name="{q[0]}" id="rep{q[0]}" /> <label for="rep{q[0]}">{q[1]}</label><br />'
    return render_template('formulaire.html', n = q_en_cours, question=questions[q_en_cours][0], quizz=Markup(quizzstr))

@app.route('/reponse.html', methods=["POST"])
def reponse():
    reponse = request.form
    q = int(reponse["n_quest"])
    if questions[q][2]:
        n = reponse["repcu"]
        ajoute_reponse(q, n)
    else:
        n = []
        for r in questions[q][1]:
            if r[0] in reponse:
                n.append(r[0])
                ajoute_reponse(q, r[0])
    return render_template('reponse.html', reponse=n, question = questions[q][0], n_quest=q)

#
# Bilans 
#

@app.route('/bilan.html', methods=["GET"])
def bilan():
    """Bilan final avec reponses et scores"""
    n_quest_form = request.args
    n_quest = int(n_quest_form["q"])
    if n_quest in reponses:
        bilstr = '<ul>'
        for q in questions[n_quest][1]:
            if q[0] in reponses[n_quest] :
                bilstr += f"<li>{q[1]} : {reponses[n_quest][q[0]]}</li>"
            else:
                bilstr += f"<li>{q[1]} : 0</li>"
        bilstr += '</ul>'
        questionstr = questions[n_quest][0]
    else:
        bilstr = "<p>Pas de réponses encore à la question"
        questionstr = questions[n_quest][0] if n_quest in questions else "Plus de question !!"
    return render_template('bilan.html', q=n_quest, question=questionstr, resultats=Markup(bilstr))

@app.route('/bilan1.html', methods=["GET"])
def bilan1():
    """Bilan intermediaire avec reponses masquees"""
    n_quest_form = request.args
    n_quest = int(n_quest_form["q"])
    if n_quest in reponses:
        replist = []
        for q in questions[n_quest][1]:
            if q[0] in reponses[n_quest] :
                replist.append(reponses[n_quest][q[0]])
            else:
                replist.append(0)
        replist.sort()
        bilstr = "<ul>"
        for r in replist:
            bilstr += f"<li>{r}</li>"
            questionstr = questions[n_quest][0]
        bilstr += "</ul>"
    else:
        bilstr = "<p>Pas de réponses encore à la question"
        questionstr = questions[n_quest][0] if n_quest in questions else "Plus de question !!"
    return render_template('bilan.html', q=n_quest, question=questionstr, resultats=Markup(bilstr))

app.run(debug=False)

# http://localhost:5000
