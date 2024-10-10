from sqlalchemy.sql import text
from db import db
from datetime import datetime

def listar_productos_arballon():
    # cambiar a sqlserver para llamar a arballon
    try:
        with db.db.get_engine(bind='sqlserver').connect() as connection:
            result = connection.execute(text("""
                SELECT cod_mae, den, cod_cls FROM genmae
                WHERE tip_mae = 4 AND (
                    cod_cls = 'Extrac' OR
                    cod_cls = 'Pas500' OR
                    cod_cls = 'Pelado' OR
                    cod_cls = 'Pulpa' OR
                    cod_cls = 'Pure' OR
                    cod_cls = 'Tri500' OR
                    cod_cls = 'Tri8' OR
                    cod_cls = 'Tri910' OR
                    cod_cls = 'Tri950' OR
                    cod_cls = 'Tritur'
                )
            """))
            return result.fetchall()

    except Exception as e:
        print(f"Error: {e}")
        return None

def get_ultimo_id():
    try:
        sql = text("""
                    SELECT numero_unico
                    FROM mercaderia
                    ORDER BY id DESC
                    LIMIT 1
                   ;
                """
                )
        
        result = db.db.session.execute(sql)
        
        ultimo_id = result.scalar()
        
        if not ultimo_id:
            # si es el primer pallet
            year = datetime.now().year
            return f"{year}-T-000000"
        else:
            # si ya existen pallets, aumentar el numero del id
            prefijo = ultimo_id[:-6]
            sufijo = int(ultimo_id[-6:])
            nuevo_numero = sufijo + 1
            nuevo_numero_str = f"{nuevo_numero:06d}"
            nuevo_codigo = prefijo + nuevo_numero_str
            return nuevo_codigo
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_vencimiento(form):
    try:
        sql = text("""
                    SELECT *
                    FROM vencimiento
                    WHERE producto = :producto
                    ORDER BY id DESC;
                """
                )
        
        vencimiento = db.db.session.execute(sql,{"producto": form["cod_cls"]})
        return vencimiento.mappings().first()
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_vencimiento_meses(vto_id):
    try:
        sql = text("""
                    SELECT *
                    FROM vencimiento
                    WHERE id = :id
                """
                )
        
        vencimiento = db.db.session.execute(sql,{"id": vto_id})
        return vencimiento.mappings().first()
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def insert_mercaderia(form, vto):
    
    try:
        sql = text("""
                    INSERT INTO
                    mercaderia
                    (producto, observacion, cantidad, lote, fecha_elaboracion, 
                    responsable, numero_unico, vto, fecha_registro,
                    antecedentes)
                    VALUES
                    (:producto, :observacion, :cantidad, :lote, :fecha_elaboracion, 
                    :responsable, :numero_unico, :vto, CURRENT_TIMESTAMP,
                    :antecedentes)
                """
                )
        
        vencimiento = db.db.session.execute(sql,
                                            {
                                                "producto": form['cod_mae'],
                                                "observacion": form['observaciones'],
                                                "cantidad": form['cantidad'],
                                                "lote": form['lote'],
                                                "fecha_elaboracion": f"{form['fecha']} {form['hora']}",
                                                "responsable": form['user_id'],
                                                "numero_unico": form['numero_unico'],
                                                "vto": vto['id'],
                                                "antecedentes": form['antecedentes'],
                                            })
        db.db.session.commit()
        return True
    except Exception as e:
        db.db.session.rollback()
        print(f"Error: {e}")
        return None
    
def get_envasado(numero_unico):
    try:
        sql = text("""
                    SELECT *
                    FROM mercaderia
                    WHERE numero_unico = :numero_unico
                """
                )
        
        vencimiento = db.db.session.execute(sql,{"numero_unico": numero_unico})
        return vencimiento.mappings().first()
    except Exception as e:
        print(f"Error: {e}")
        return None