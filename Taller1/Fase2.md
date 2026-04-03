# Fase 2. Evaluación de fortalezas, limitaciones y riesgos éticos

En esta fase se realiza un análisis crítico de las implicaciones asociadas a la implementación de la solución híbrida propuesta para EcoMarket, considerando aspectos como las alucinaciones, los sesgos, la privacidad de los datos y el impacto sobre los trabajadores.

## 2.1 Fortalezas de la solución propuesta

Una de las principales fortalezas de la solución es la reducción del tiempo de respuesta. EcoMarket actualmente tiene un promedio de respuesta de 24 horas, y dado que el 80% de las consultas son repetitivas, una solución automatizada podría atender gran parte de estas solicitudes en pocos segundos o minutos. Esto tendría un impacto directo en la satisfacción del cliente y en la eficiencia del área de soporte.

Otra fortaleza importante es la disponibilidad 24/7. A diferencia de un equipo exclusivamente humano, el sistema podría atender consultas en cualquier horario, incluyendo noches, fines de semana y festivos. Esto es especialmente valioso en comercio electrónico, donde los clientes esperan respuestas rápidas sin importar el momento en que escriban.

También destaca la capacidad para manejar de forma consistente las consultas frecuentes. La solución permitiría responder de forma uniforme preguntas sobre pedidos, devoluciones y productos, disminuyendo la variabilidad en la atención y asegurando que la información entregada siga las políticas de la empresa. Además, al integrarse con bases de datos internas, las respuestas tendrían mayor precisión que un modelo que respondiera solo con conocimiento general.

Finalmente, la solución tiene la fortaleza de optimizar el trabajo del equipo humano. Al encargarse de las consultas simples y repetitivas, libera a los agentes para que se concentren en problemas complejos, reclamos sensibles o situaciones que requieren empatía y juicio humano. En ese sentido, la IA generativa actúa como una herramienta de apoyo operativo y no solo como un mecanismo de automatización.

## 2.2 Limitaciones de la solución propuesta

A pesar de sus beneficios, la solución también presenta limitaciones importantes. La primera es que no puede sustituir completamente la atención humana. El propio caso indica que existe un 20% de solicitudes complejas que requieren toque humano y empatía, como quejas, problemas técnicos o sugerencias. En este tipo de interacciones, un modelo puede resultar insuficiente o poco apropiado si el cliente necesita contención, flexibilidad o negociación.

Otra limitación es la dependencia de la calidad de la información interna. Si la base de pedidos, el sistema de devoluciones o el catálogo contienen errores, están desactualizados o incompletos, el modelo responderá con información incorrecta. Es decir, aunque el LLM funcione bien desde el punto de vista conversacional, la calidad del resultado seguirá dependiendo de la calidad del dato empresarial.

Además, la solución puede tener dificultades con consultas ambiguas o mal formuladas. Algunos clientes pueden mezclar varios temas en el mismo mensaje, omitir información clave o expresarse de manera emocional o confusa. En estos casos, el sistema puede clasificar mal la intención o construir una respuesta insuficiente.

Por último, existe una limitación operativa relacionada con la necesidad de monitoreo continuo. La solución no puede considerarse definitiva una vez implementada; requiere revisión constante de logs, evaluación de errores, actualización de políticas y mejora progresiva de prompts y reglas de escalamiento.

## 2.3 Riesgos éticos de la solución

### Alucinaciones

Uno de los riesgos éticos más importantes es la posibilidad de que el modelo invente información sobre pedidos, productos o devoluciones. Por ejemplo, podría generar una fecha de entrega incorrecta, afirmar que un producto sí admite devolución cuando no es cierto, o dar características erróneas del catálogo. En un entorno de atención al cliente, esto puede generar desinformación, frustración y pérdida de confianza por parte del usuario.

Para mitigar este problema, la solución debe responder solo con base en información recuperada desde sistemas internos confiables. Cuando no exista contexto suficiente o la confianza en la respuesta sea baja, el caso debe escalar a un agente humano en lugar de permitir que el modelo improvise.

### Sesgo

Otro riesgo ético es el sesgo algorítmico. El modelo podría ofrecer respuestas más útiles a ciertos tipos de usuarios y menos adecuadas a otros, dependiendo del lenguaje utilizado, el estilo de escritura o patrones presentes en sus datos de entrenamiento. Esto podría traducirse en diferencias injustas en la calidad del servicio.

La mitigación requiere probar la solución con perfiles diversos de usuarios, revisar si existen patrones de trato desigual y ajustar prompts o criterios de clasificación cuando sea necesario.

### Privacidad de datos

La privacidad de los datos del cliente es otro riesgo crítico. Para responder adecuadamente, el sistema podría acceder a datos sensibles como nombre, dirección, historial de compras, estado del pedido o motivo de devolución. Si esa información no se maneja con controles adecuados, se pueden producir exposiciones indebidas o usos no autorizados.

Para mitigar este riesgo, la empresa debería aplicar principios de minimización de datos, acceso restringido, anonimización cuando sea posible y políticas claras sobre qué información puede utilizarse en prompts o procesos de mejora del sistema.

### Impacto laboral

También existe un riesgo relacionado con el impacto laboral sobre los agentes de servicio al cliente. Si la implementación se plantea únicamente como una sustitución de personas, podría generar resistencia, desmotivación o deterioro del clima laboral.

En este caso, la propuesta debe entenderse como una herramienta para empoderar al equipo humano, liberándolo de tareas repetitivas y permitiéndole concentrarse en casos más complejos, de mayor valor y con mayor componente humano.

En conclusión, la solución híbrida propuesta para EcoMarket ofrece fortalezas claras en rapidez, disponibilidad, consistencia y eficiencia operativa. Sin embargo, también presenta limitaciones importantes y riesgos éticos que deben gestionarse de forma responsable. Para que la implementación sea exitosa, no basta con que el modelo responda bien; también es necesario garantizar calidad de datos, supervisión humana, protección de la privacidad, revisión de sesgos y una estrategia organizacional que complemente, y no reemplace sin criterio, el trabajo de los agentes.
