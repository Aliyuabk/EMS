from app import create_app, db
from app.models import User, Zone, School

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Zone': Zone, 'School': School}

if __name__ == '__main__':
    app.run(debug=True)
