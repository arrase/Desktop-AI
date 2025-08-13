# Descripción de la aplicación

Gestor de tareas programadas para linux escrito en PyQT.

# Implementación

## Interface gráfica

La aplicación se inicia cuando el usuario arranca sesión en su entorno gráfico.
Al iniciar la aplicación queda anclada en el system tray.
Al pulsar el botón derecho del ratón sobre el icono de la aplicación en el system tray debe aparecer un menu contextual con dos entradas, una para detener la aplicación y otra donde se abrirá la venta de configuración de la aplicación.
La aplicación solo se oodra detener al usar el menú contextual, intentar cerrar la ventana desde el entorno gráfico como se hace usualmente debe minimizarla en el system tray en lugar de cerrarla.
Desde la venta de configuración se podra deleccionar en que directorio se va a guardar la base de datos sqlite que se usara para persistir los datos de la aplicación, por defecto debe ser un directorio dentro de ~/.config.
Al pulsar con el botón izquierdo del ratón sobre el icono de la aplicación en el system tray se abrira la pantalla principal.
La Venta principal debe mostrar las tareas guardadas por el usuario en formato lista de tarjetas.
Cada tarjeta muestra el texto de la tarea y un boton para borrar individualmente las tareas.
La venta principal tendra un boton para añadir nuevas tareas.
La pantalla para añadir una nueva tarea consta de dos cajas de texto, una para describí con que frecuencia se ha de ejecutar la tarea y otra para describir la tarea a realizar.

## Reglas para el código

Se debe estructurar el proyecto para ser instlado con seruptools
El código ha de ser lo mas limpio y conciso posible.
Se usara la librería de python PyQT para su implementación.
