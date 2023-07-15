import sqlite3
from flask import Flask,  jsonify, request

#imporamos la conexion
from conexion import get_db_connection

#importamos las clases desde otros Archivos
from ProductoClass import Producto

#Class Inventario
class Inventario:
    def __init__(self):
        self.conexion = get_db_connection()
        self.cursor = self.conexion.cursor()

    def agregar_producto(self, codigo, descripcion, cantidad, precio):
        producto_existente = self.consultar_producto(codigo)
        if producto_existente:
            return jsonify({'message': 'Ya existe un producto con ese código.'}), 400
        
        try:
            #nuevo_producto = Producto(codigo, descripcion, cantidad, precio)
            self.cursor.execute("INSERT INTO productos VALUES (?, ?, ?, ?)", (codigo, descripcion, cantidad, precio))
            self.conexion.commit()
            return jsonify({'message': 'Producto agregado correctamente.'}), 200
        
        except sqlite3.Error as e:            
            print("Error al consultar la base de datos:", e)
            return jsonify({'error': 'Error al consultar la base de datos: '+ e}), 500

    def consultar_producto(self, codigo):
        try:
            self.cursor.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,))
            row = self.cursor.fetchone()
            if row:
                codigo, descripcion, cantidad, precio = row
                return Producto(codigo, descripcion, cantidad, precio)
            return None
        
        except sqlite3.Error as e:            
            print("Error al consultar la base de datos:", e)
            return jsonify({'error': 'Error al consultar la base de datos: '+ e}), 500

    def modificar_producto(self, codigo, nueva_descripcion, nueva_cantidad, nuevo_precio):
        producto = self.consultar_producto(codigo)
        if producto:
            try:
                producto.modificar(nueva_descripcion, nueva_cantidad, nuevo_precio)
                self.cursor.execute("UPDATE productos SET descripcion = ?, cantidad = ?, precio = ? WHERE codigo = ?",
                                    (nueva_descripcion, nueva_cantidad, nuevo_precio, codigo))
                self.conexion.commit()
                return jsonify({'message': 'Producto modificado correctamente.'}), 200
            
            except sqlite3.Error as e:            
                print("Error al consultar la base de datos:", e)
                return jsonify({'error': 'Error al consultar la base de datos: '+ e}), 500
            
        return jsonify({'message': 'Producto no encontrado.'}), 404

    def listar_productos(self):
        try:
            self.cursor.execute("SELECT * FROM productos")
            rows = self.cursor.fetchall()
            productos = []
            for row in rows:
                codigo, descripcion, cantidad, precio = row
                producto = {'codigo': codigo, 'descripcion': descripcion, 'cantidad': cantidad, 'precio': precio}
                productos.append(producto)
            return jsonify(productos), 200
            
        except sqlite3.Error as e:            
            print("Error al consultar la base de datos:", e)
            return jsonify({'error': 'Error al consultar la base de datos: '+ e}), 500

    def eliminar_producto(self, codigo):
        try:
            self.cursor.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
            if self.cursor.rowcount > 0:
                self.conexion.commit()
                return jsonify({'message': 'Producto eliminado correctamente.'}), 200
            return jsonify({'message': 'Producto no encontrado.'}), 404
        
        except sqlite3.Error as e:            
            print("Error al consultar la base de datos:", e)
            return jsonify({'error': 'Error al consultar la base de datos: '+ e}), 500