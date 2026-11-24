import os
from datetime import datetime, timezone

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

basedir = os.path.abspath(os.path.dirname(__file__))

# Dados do aluno exibidos na rota principal
ALUNO_NOME = 'Guilherme Souto Silva'
ALUNO_PRONTUARIO = 'PT3038483'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-avaliacao')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

DISCIPLINAS = ['DSWA5', 'GPSA5', 'IHCA5', 'SODA5', 'PJIA5', 'TCOA5']


class Professor(db.Model):
    __tablename__ = 'professores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), nullable=False)
    disciplina = db.Column(db.String(16), nullable=False)

    def __repr__(self):
        return f'<Professor {self.nome}>'


class ProfessorForm(FlaskForm):
    name = StringField('Cadastre o novo Professor:', validators=[DataRequired()])
    role = SelectField('Disciplina associada:', choices=[(d, d) for d in DISCIPLINAS])
    submit = SubmitField('Cadastrar')


with app.app_context():
    db.create_all()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Professor=Professor)


# ---------- Tratamento de erros ----------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# ---------- Rotas ----------
@app.route('/')
def index():
    return render_template('index.html',
                           nome=ALUNO_NOME,
                           prontuario=ALUNO_PRONTUARIO,
                           current_time=datetime.now(timezone.utc))


@app.route('/professores', methods=['GET', 'POST'])
def professores():
    form = ProfessorForm()
    if form.validate_on_submit():
        professor = Professor(nome=form.name.data, disciplina=form.role.data)
        db.session.add(professor)
        db.session.commit()
        return redirect(url_for('professores'))
    lista = Professor.query.order_by(Professor.id).all()
    return render_template('professores.html', form=form, professores=lista)


# Módulos não desenvolvidos
@app.route('/disciplinas')
@app.route('/alunos')
@app.route('/cursos')
@app.route('/ocorrencias')
def nao_disponivel():
    return render_template('nao_disponivel.html',
                           current_time=datetime.now(timezone.utc))


if __name__ == '__main__':
    app.run(debug=True)
