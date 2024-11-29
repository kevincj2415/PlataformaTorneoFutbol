# Plataforma de Torneos de Fútbol

## Descripción

La **Plataforma de Torneos de Fútbol** es una aplicación web construida con **Flask**, **MongoDB** y otras tecnologías modernas. Permite a los usuarios gestionar torneos, partidos y notificaciones de forma sencilla. Los usuarios pueden ver torneos activos, consultar partidos programados y recibir notificaciones sobre actualizaciones importantes de la plataforma. 

Este proyecto está diseñado para ser altamente escalable, fácil de usar y mantener, utilizando las mejores prácticas de desarrollo web y diseño de interfaces.

## Funcionalidades

### **Usuarios**
- **Registro de usuarios**: Los usuarios pueden registrarse proporcionando un correo electrónico y una contraseña.
- **Inicio de sesión**: Los usuarios registrados pueden iniciar sesión con su correo electrónico y contraseña.
- **Cerrar sesión**: Los usuarios autenticados pueden cerrar sesión de forma segura.

### **Gestión de Torneos**
- **Ver torneos**: Los usuarios pueden visualizar los torneos activos en la plataforma.
- **Crear torneos**: Los administradores pueden crear nuevos torneos especificando los detalles, como el nombre, las fechas de inicio y fin, y el formato del torneo.
- **Detalles del torneo**: Los usuarios pueden ver detalles específicos de cada torneo.

### **Gestión de Partidos**
- **Ver partidos programados**: Los usuarios pueden consultar todos los partidos programados.
- **Crear partidos**: Los administradores pueden crear partidos dentro de un torneo, indicando los equipos participantes, la fecha y el resultado (después de que se juegue el partido).

### **Notificaciones**
- **Ver notificaciones**: Los usuarios reciben notificaciones sobre cambios importantes en torneos y partidos.
- **Marcar notificaciones como leídas**: Los usuarios pueden marcar las notificaciones como leídas.
  
### **Público sin autenticación**
- Los usuarios pueden ver los torneos y partidos disponibles sin necesidad de iniciar sesión.

## Tecnologías Utilizadas

- **Flask**: Framework web para Python que facilita el desarrollo de aplicaciones web ligeras y escalables.
- **MongoDB Atlas**: Base de datos NoSQL utilizada para almacenar los datos de torneos, partidos, usuarios y notificaciones.
- **Flask-PyMongo**: Librería para conectar Flask con MongoDB.
- **Flask-Bcrypt**: Librería para encriptar las contraseñas de los usuarios.
- **Flask-Login**: Librería para manejar la autenticación de usuarios.
- **Jinja2**: Motor de plantillas para generar dinámicamente el HTML.
- **HTML/CSS**: Lenguajes utilizados para diseñar las páginas web.

## Requisitos

Asegúrate de tener estas librerías instaladas en tu entorno para ejecutar el proyecto correctamente.

```bash
pip install -r requirements.txt
