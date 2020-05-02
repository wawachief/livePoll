# Auteur : Olivier Lecluse
# Mai 2020
# Licence GPL-3.0-or-later

from flask import Flask, render_template, request, Markup, redirect, url_for, send_file
from requests import get
import io
import qrcode
from liste_questions import questions

app = Flask(__name__)

reponses = dict()

# Parametrage IP
# Recuperer l'IP publique automatiquement
ip_pub = get('https://api.ipify.org').text
port_pub = 5000 # port public
# machines autorisees pour administration
ip_admin = ["127.0.0.1"]

q_en_cours = 0
new_quest = False
# Affichage blocs supplementaires dans bilan
quest_enable = True  # Rappel question dans bilan
qrcode_enable = True

#
# Fabrication QRCode
#

@app.route('/qrcode.png')
def qrcode_png():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2,
    )
    qr.add_data(f"http://{ip_pub}:{port_pub}/")
    qr.make(fit=True)
    output = io.BytesIO()
    qrcode_img = qr.make_image(fill_color="black", back_color="white")
    qrcode_img.get_image().save(output, format='PNG')
    output.seek(0, 0)
    return send_file(output, mimetype='image/png', as_attachment=False)

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
    # Securisation de la page
    host = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if host not in ip_admin:
        return 

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
    # Securisation de la page
    host = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if host not in ip_admin:
        return 
        
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
    for (nq,q) in enumerate(questions[q_en_cours][1]):
        if questions[q_en_cours][2]:
            quizzstr += f'<input type="radio" name="repcu" value="{nq}" id="rep{nq}" /> <label for="rep{nq}">{q}</label><br />'
        else:
            quizzstr += f'<input type="checkbox" name="{nq}" id="rep{nq}" /> <label for="rep{nq}">{q}</label><br />'
    return render_template('formulaire.html', n = q_en_cours, question=questions[q_en_cours][0], quizz=Markup(quizzstr))

@app.route('/reponse.html', methods=["POST"])
def reponse():
    global new_quest
    new_quest = False
    reponse = request.form
    q = int(reponse["n_quest"])
    # Question de type QCU
    if questions[q][2]:
        n = int(reponse["repcu"])
        ajoute_reponse(q, n)
    else:
        # Question de type QCM
        n = []
        for (nr,r) in enumerate(questions[q][1]):
            if str(nr) in reponse:
                n.append(nr)
                ajoute_reponse(q, nr)
    return render_template('reponse.html', reponse=n, question = questions[q][0], n_quest=q)

#
# Bilans 
#

def recupere_params_get(req):
    try:
        n_quest_form = req.args
        n_quest = int(n_quest_form.get("q",1))
    except:
        n_quest = 1
        hidden = 1
    else:
        hidden = int(n_quest_form.get("hidden",1))
    return n_quest, hidden

@app.route('/bilan_list', methods=["GET"])
def bilan_list():
    """Appel ajax bilan
        appel avec parametres get
        - q : no de question
        - hidden (0 ou 1) intitulkes masques"""

    # Securisation de la page
    host = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if host not in ip_admin:
        return 

    n_quest, hidden = recupere_params_get(request)
    
    # Liste des reponses 
    if n_quest in reponses:
        replist = []
        bilstr = '<ul>'
        for (nq,q) in enumerate(questions[n_quest][1]):
            nb_reponses = reponses[n_quest].get(nq, 0)
            if hidden == 1: 
                replist.append(nb_reponses)
            else:
                bilstr += f"<li>{q} : {nb_reponses}</li>"
        if hidden == 1:
            replist.sort()
            for r in replist:
                bilstr += f"<li>{r}</li>"
        bilstr += '</ul>'
    else:
        bilstr = "<p>Pas de réponses encore à la question</p>"
    return Markup(bilstr)
    
@app.route('/bilan', methods=["GET"])
def bilan():
    """Bilan final avec scores """

    # Securisation de la page
    host = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if host not in ip_admin:
        return 

    # Recuperation no question
    n_quest, hidden = recupere_params_get(request)
    
    questionstr = questions[n_quest][0] if n_quest in questions else "Plus de question !!"

    # Rappel de la question
    quest_html = ""
    if quest_enable and n_quest in questions:
        quest_html = f"<ul>"
        for r in questions[n_quest][1]:
            quest_html += f"<li>{r}</li>"
        quest_html += "</ul>"
    
    # Affichage qrcode
    qrcode_html = ""
    if qrcode_enable:
        qrcode_html = f"<img src=\"{url_for('qrcode_png')}\" class=\"qrcode\" >"
    return render_template('bilan.html', q = n_quest, question = questionstr,
        qrcode = Markup(qrcode_html), quest = Markup(quest_html), hide = hidden)


@app.route('/bilan_reptoggle', methods=["GET"])
@app.route('/bilan_qrtoggle', methods=["GET"])
@app.route('/bilan2', methods=["GET"])
def bilan2():
    """Reinitialisation du bilan"""
    global qrcode_enable, quest_enable

    # Securisation de la page
    host = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if host not in ip_admin:
        return 

    bilan2 =  "bilan2" in str(request.url)
    qr =  "qrtoggle"   in str(request.url)
    rep =  "reptoggle" in str(request.url)
    
    n_quest, _ = recupere_params_get(request)

    if qr:
        qrcode_enable = not qrcode_enable
    if rep:
        quest_enable = not quest_enable
    if bilan2 and n_quest in reponses:
        reponses[n_quest].clear()
    return redirect(url_for('bilan') + f"?q={n_quest}&hidden=1")

#
# Lancement de l'application
#

app.run(host= '0.0.0.0')

# http://ip_serveur:5000
