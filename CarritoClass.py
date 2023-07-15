import sqlite3
from flask import Flask,  jsonify, request

#imporamos la conexion
from conexion import get_db_connection

#importamos las clases desde otros Archivos
from ProductoClass import Producto

#Class Carrito
class Carrito:
    def __init__(self):
        self.conexion = get_db_connection()
        self.cursor = self.conexion.cursor()
        self.items = []

    def agregar(self, codigo, cantidad, inventario):
        producto = inventario.consultar_producto(codigo)
        if producto is None:
            return jsonify({'message': 'El producto no existe.'}), 404
        if producto.cantidad < cantidad:
            return jsonify({'message': 'Cantidad en stock insuficiente.'}), 400

        for item in self.items:
            if item.codigo == codigo:
                item.cantidad += cantidad
                try:
                    self.cursor.execute("UPDATE productos SET cantidad = cantidad - ? WHERE codigo = ?",
                                        (cantidad, codigo))
                    self.conexion.commit()
                    return jsonify({'message': 'Producto agregado al carrito correctamente.'}), 200
                
                except sqlite3.Error as e:            
                    print("Error al consultar la base de datos:", e)
                    return jsonify({'error': 'Error al consultar la base de datos: '+ e}), 500

        nuevo_item = Producto(codigo, producto.descripcion, cantidad, producto.precio)
        self.items.append(nuevo_item)
        try:
            self.cursor.execute("UPDATE productos SET cantidad = cantidad - ? WHERE codigo = ?",
                                (cantidad, codigo))
            self.conexion.commit()
            return jsonify({'message': 'Producto agregado al carrito correctamente.'}), 200
        
        except sqlite3.Error as e:            
            print("Error al consultar la base de datos:", e)
            return jsonify({'error': 'Error al consultar la base de datos: '+ e}), 500

    def quitar(self, codigo, cantidad, inventario):
        for item in self.items:
            if item.codigo == codigo:
                if cantidad > item.cantidad:
                    return jsonify({'message': 'Cantidad a quitar mayor a la cantidad en el carrito.'}), 400
                item.cantidad -= cantidad
                if item.cantidad == 0:
                    self.items.remove(item)
                try:
                    self.cursor.execute("UPDATE productos SET cantidad = cantidad + ? WHERE codigo = ?",
                                        (cantidad, codigo))
                    self.conexion.commit()
                    return jsonify({'message': 'Producto quitado del carrito correctamente.'}), 200
                
                except sqlite3.Error as e:            
                    print("Error al consultar la base de datos:", e)
                    return jsonify({'error': 'Error al consultar la base de datos: '+ e}), 500

        return jsonify({'message': 'El producto no se encuentra en el carrito.'}), 404

    def mostrar(self):
        productos_carrito = []
        for item in self.items:
            producto = {'codigo': item.codigo, 'descripcion': item.descripcion, 'cantidad': item.cantidad,
                        'precio': item.precio}
            productos_carrito.append(producto)
        return jsonify(productos_carrito), 200