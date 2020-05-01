# Auteur : Olivier Lecluse
# Mai 2020
# Licence GPL v3 : https://www.gnu.org/licenses/quick-guide-gplv3.fr.html

from flask import Flask, render_template, request, Markup, redirect, url_for

app = Flask(__name__)

questions = {
    # No : [ Question, [(code, reponse), ( , )...], QCU?QCM]
    1 : ["Question Vrai / Faux", 
		[('A', "Vrai"), ('B', "Faux")],
		True],
	2 : ["Question Oui / Non", 
		[('A', "Oui"), ('B', "Non")],
		True],
	3 : ["Choix unique A B C D", 
		[('A', "Réponse A"), ('B', "Réponse B"), ('C', "Réponse C"), ('D', "Réponse D")],
		True],
	4 : ["Choix multiple QCM A B C D", 
		[('A', "Réponse A"), ('B', "Réponse B"), ('C', "Réponse C"), ('D', "Réponse D")],
		False]
}

reponses = dict()

q_en_cours = 0
new_quest = False

def ajoute_reponse(q, r):
    """Ajoute une reponse r à la question q"""
    if not q in reponses:
        reponses[q] = dict()
    reponses[q][r] = reponses[q].get(r, 0) + 1

@app.route('/', methods=["GET"])
@app.route('/index.html', methods=["GET"])
def index():
    try:
        n_quest_form = request.args
        n_quest = int(n_quest_form["q"])
    except:
        n_quest = 0
    if q_en_cours == 0 or (q_en_cours == n_quest and not new_quest):
        return render_template('index.html')
    else:
        return redirect(url_for('formulaire'))

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
    global q_en_cours, new_quest
    reponse = request.form
    q_en_cours = int(reponse["n_quest"])
    new_quest = True
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
    global new_quest
    new_quest = False
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

@app.route('/bilan1', methods=["GET"])
@app.route('/bilan', methods=["GET"])
def bilan():
    """Bilan final avec scores """
    try:
        n_quest_form = request.args
        n_quest = int(n_quest_form["q"])
    except:
        n_quest = 1
    # Reponses masquees
    hidden =  "bilan1" in str(request.url)
    refresh_cmd = '<meta http-equiv="refresh" content="3" />' if hidden else ''

    if n_quest in reponses:
        replist = []
        bilstr = '<ul>'
        for q in questions[n_quest][1]:
            nb_reponses = reponses[n_quest].get(q[0], 0)
            if hidden : 
                replist.append(nb_reponses)
            else:
                bilstr += f"<li>{q[1]} : {nb_reponses}</li>"
        if hidden:
            replist.sort()
            for r in replist:
                bilstr += f"<li>{r}</li>"
                questionstr = questions[n_quest][0]
        bilstr += '</ul>'
        questionstr = questions[n_quest][0]
    else:
        bilstr = "<p>Pas de réponses encore à la question</p>"
        questionstr = questions[n_quest][0] if n_quest in questions else "Plus de question !!"
    return render_template('bilan.html', q=n_quest, question=questionstr, 
        resultats=Markup(bilstr), refresh=Markup(refresh_cmd))

@app.route('/bilan2', methods=["GET"])
def bilan2():
    """Bilan intermediaire avec reponses masquees"""
    try:
        n_quest_form = request.args
        n_quest = int(n_quest_form["q"])
    except:
        n_quest = 0
    if n_quest in reponses:
        reponses[n_quest].clear()
    return redirect(url_for('bilan') + f"1?q={n_quest}")

app.run(host= '0.0.0.0')

# http://ip_serveur:5000
