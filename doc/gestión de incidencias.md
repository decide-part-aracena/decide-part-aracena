**1. RESUMEN EJECUTIVO**

El equipo ha decidido el siguiente método para gestionar las incidencias, ya sea para describir la petición para añadir un incremento o la solucionar un problema. 

**2. SISTEMA DE GESTIÓN**

Utilizamos github como herramienta para gestionar tanto el proyecto como las incidencias que lo componen para así tenerlos vinculados al repositorio. Las incidencias se crean desde el menú Issues donde, a continuación, detallamos los campos a completar.

**3. CONTENIDO DE LA INCIDENCIA**

Título: descripción clara y concisa sobre la información de la incidencia.

Identificador: número generado de forma ordinal por github. Usado para vincular commits a una incidencia determinada.

Comentario: descripción más detallada de la incidencia. 

Asignación: miembros del equipo encargados de gestionar la incidencia.

Etiquetas: 
El equipo decidió crear etiquetas personalizadas para agrupar las incidencias en función del subsistema al que se le va a hacer un incremento. Por ejemplo:
  - Autenticación.
  - Censo.
  - Visualización.
Además, se añadieron las siguientes:
  - Epic: indica que la incidencia se ha dividido en otras para facilitar su desarrollo.
  - documentation: gestión de documentos del proyecto.
  - CI/CD: incidencias relacionadas con la adaptación del proyecto a la Integración contínua.
  
Por otro lado, utilizamos algunas de las que github añade por defecto:
  - bug: fallo de programación en el software.
  - duplicate: ya hay otra incidencia similar.
  - enhancement: solicitud de mejora en el software.
  - good first issue: idonea para un desarrollador del equipo junior.
  - help wanted: petición de ayuda.
  - invalid: la incidencia carece de sentido.
  - question: pregunta a responder por el equipo de desarrollo.
  - wontix: comportamiento defectuoso / no existe solución posible.

Proyecto (y estado): vinculamos la incidencia al proyecto correspondiente y le asignamos un estado.
  Estados: 
    - Todo: incidencia por hacer.
    - In Progress: se ha comenzado a trabajar en ella.
    - Review: esperando a ser revisada.
    - Testing: desarrollo de las pruebas.
    - Done: considerada como hecha.

Milestone: hito para agrupar las diferentes incidencias que deben estar listas para una fecha de entrega determinada.

Desarrollo: rama y pull request asociada a la incidencia.
