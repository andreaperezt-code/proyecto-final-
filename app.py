"""
🐾 Animales Perdidos - Backend Flask
Aplicación web para reportar y encontrar mascotas perdidas
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import base64
import json

# Ruta del archivo JSON
DATA_FILE = 'data/reportes.json'

# Configuración
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-animales-perdidos-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///animales.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== FUNCIONES JSON ====================

def guardar_en_json():
    """Sincroniza todos los reportes de la BD al archivo JSON"""
    reportes = Reporte.query.all()
    datos = []
    for r in reportes:
        datos.append({
            'id': r.id,
            'nombre': r.nombre,
            'descripcion': r.descripcion,
            'categoria': r.categoria,
            'fecha_perdido': r.fecha_perdido.strftime('%Y-%m-%d') if r.fecha_perdido else '',
            'ubicacion': r.ubicacion,
            'contacto': r.contacto,
            'estado': r.estado,
            'foto': r.foto,
            'fecha_reporte': r.fecha_reporte.strftime('%Y-%m-%d %H:%M') if r.fecha_reporte else '',
            'comentario_estado': r.comentario_estado
        })
    
    # Crear carpeta data si no existe
    os.makedirs('data', exist_ok=True)
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Datos guardados en {DATA_FILE} ({len(datos)} reportes)")


# ==================== MODELOS ====================

class Reporte(db.Model):
    """Modelo para reportes de animales perdidos"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(50), default='otro')
    fecha_perdido = db.Column(db.Date, nullable=False)
    ubicacion = db.Column(db.String(200), nullable=False)
    contacto = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(20), default='Perdido')
    foto = db.Column(db.Text)
    fecha_reporte = db.Column(db.DateTime, default=datetime.utcnow)
    comentario_estado = db.Column(db.Text)
    
    comentarios = db.relationship('Comentario', backref='reporte', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria': self.categoria,
            'fecha_perdido': self.fecha_perdido.strftime('%Y-%m-%d') if self.fecha_perdido else '',
            'ubicacion': self.ubicacion,
            'contacto': self.contacto,
            'estado': self.estado,
            'foto': self.foto,
            'fecha_reporte': self.fecha_reporte.strftime('%d/%m/%Y %H:%M') if self.fecha_reporte else '',
            'comentario_estado': self.comentario_estado
        }


class Comentario(db.Model):
    """Modelo para comentarios"""
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    reporte_id = db.Column(db.Integer, db.ForeignKey('reporte.id'), nullable=False)


# ==================== RUTAS ====================

@app.route('/')
def index():
    """Página de inicio"""
    reportes = Reporte.query.all()
    total = len(reportes)
    encontrados = len([r for r in reportes if r.estado == 'Encontrado'])
    perdidos = len([r for r in reportes if r.estado in ['Perdido', 'Visto']])
    return render_template('index.html', total=total, encontrados=encontrados, perdidos=perdidos)


@app.route('/reportar', methods=['GET', 'POST'])
def reportar():
    """Crear nuevo reporte"""
    if request.method == 'POST':
        foto_base64 = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and foto.filename:
                foto_data = foto.read()
                foto_base64 = f"data:{foto.content_type};base64,{base64.b64encode(foto_data).decode('utf-8')}"
        
        nuevo = Reporte(
            nombre=request.form['nombre'],
            descripcion=request.form['descripcion'],
            categoria=request.form.get('categoria', 'otro'),
            fecha_perdido=datetime.strptime(request.form['fecha_perdido'], '%Y-%m-%d').date(),
            ubicacion=request.form['ubicacion'],
            contacto=request.form['contacto'],
            foto=foto_base64,
            estado='Perdido'
        )
        db.session.add(nuevo)
        db.session.commit()
        guardar_en_json()  # Sincronizar con archivo JSON
        flash('¡Reporte creado exitosamente! 🎉', 'success')
        return redirect(url_for('reportes'))
    
    return render_template('reportar.html')


@app.route('/reportes')
def reportes():
    """Lista de reportes"""
    busqueda = request.args.get('busqueda', '')
    categoria = request.args.get('categoria', '')
    estado = request.args.get('estado', '')
    
    query = Reporte.query
    if busqueda:
        query = query.filter(Reporte.nombre.ilike(f'%{busqueda}%'))
    if categoria:
        query = query.filter(Reporte.categoria == categoria)
    if estado:
        query = query.filter(Reporte.estado == estado)
    
    lista = query.order_by(Reporte.fecha_reporte.desc()).all()
    return render_template('reportes.html', reportes=lista, busqueda=busqueda, 
                          categoria_filtro=categoria, estado_filtro=estado)


@app.route('/detalle/<int:id>')
def detalle(id):
    """Detalle de un reporte"""
    reporte = Reporte.query.get_or_404(id)
    return render_template('detalle.html', reporte=reporte)


@app.route('/actualizar_estado/<int:id>', methods=['POST'])
def actualizar_estado(id):
    """Actualizar estado"""
    reporte = Reporte.query.get_or_404(id)
    nuevo_estado = request.form.get('estado')
    comentario = request.form.get('comentario', '')
    
    if nuevo_estado in ['Perdido', 'Visto', 'Encontrado']:
        reporte.estado = nuevo_estado
        if comentario:
            reporte.comentario_estado = comentario
        db.session.commit()
        guardar_en_json()  # Sincronizar con archivo JSON
        flash(f'Estado actualizado a {nuevo_estado} 🎉', 'success')
    
    return redirect(url_for('detalle', id=id))


@app.route('/agregar_comentario/<int:id>', methods=['POST'])
def agregar_comentario(id):
    """Agregar comentario"""
    texto = request.form.get('comentario', '').strip()
    if texto:
        comentario = Comentario(texto=texto, reporte_id=id)
        db.session.add(comentario)
        db.session.commit()
        flash('Comentario agregado 💬', 'success')
    return redirect(url_for('detalle', id=id))


@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    """Eliminar reporte"""
    reporte = Reporte.query.get_or_404(id)
    db.session.delete(reporte)
    db.session.commit()
    guardar_en_json()  # Sincronizar con archivo JSON
    flash('Reporte eliminado 🗑️', 'warning')
    return redirect(url_for('reportes'))


@app.route('/mapa')
def mapa():
    """Mapa de animales"""
    import json
    reportes = Reporte.query.all()
    # Preparar datos JSON para el mapa
    reportes_json = json.dumps([{
        'id': r.id,
        'nombre': r.nombre,
        'ubicacion': r.ubicacion,
        'estado': r.estado,
        'categoria': r.categoria or 'otro',
        'lat': -16.5,  # Coordenadas por defecto (La Paz, Bolivia)
        'lng': -68.15
    } for r in reportes])
    return render_template('mapa.html', reportes=reportes, reportes_json=reportes_json)


@app.route('/api/reportes')
def api_reportes():
    """API JSON"""
    lista = Reporte.query.order_by(Reporte.fecha_reporte.desc()).all()
    return jsonify([r.to_dict() for r in lista])


# ==================== INICIALIZACIÓN ====================

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("\n🐾 Animales Perdidos - Servidor Flask")
    print("=" * 40)
    print("📍 Abre: http://127.0.0.1:5000")
    print("=" * 40 + "\n")
    app.run(debug=True)
