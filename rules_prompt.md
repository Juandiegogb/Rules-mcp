## Prompt para actualización automática de reglas JS tras refactorización de modelo de datos

### Contexto del sistema

- El sistema utiliza una base de datos relacional donde las entidades (tablas) y sus campos están definidas en las tablas `syst.entitycatal` (catálogo de entidades) y `syst.entityfield` (campos de cada entidad).
- Las reglas de validación y lógica de UI para los campos de las entidades se almacenan en la tabla `syst.fieldruleglobal`, en el campo `rule`, que contiene funciones JavaScript.
- El nombre de cada función JS sigue la convención:  
  `[prefijo]_[entidad]_[campo]_[evento]`  
  Ejemplo: `global_account_payable_interest_rate_onchange`
- Dentro del código JS, también se hace referencia a los campos mediante objetos como `field.<campo>`.

### Problema

- El modelo de datos fue refactorizado: se cambiaron nombres de tablas, schemas y campos.
- Las reglas existentes en `syst.fieldruleglobal` siguen usando los nombres antiguos, tanto en el nombre de la función como en las referencias internas del código JS.
- Es necesario actualizar automáticamente estas reglas para que funcionen con los nuevos nombres.

### Ejemplo de regla antes de la refactorización

```js
function global_acpa_interest_rate_onchange(event) {
    let value = event.getValue;
    if (value == null || isNaN(value)) {
        event.setValue({ value: '', onchange: true });
        return;
    }
    value = Number(value);
    if (value < 0) {
        value = Math.abs(value);
    }
    if (value > 100) {
        value = 100;
    }
    event.setValue({ value: `${value}`, onchange: true });
    field.account_payable_interest_rate.setError({ valid: false, message: 'Error' });
}
global_account_payable_interest_rate_onchange._delay = 0
```

### Ejemplo de regla después de la refactorización (supón que la entidad ahora se llama `finance_interest` y el campo `rate` ahora es `interest_rate`)

```js
function global_account_payable_interest_rate_onchange(event) {
    let value = event.getValue;
    if (value == null || isNaN(value)) {
        event.setValue({ value: '', onchange: true });
        return;
    }
    value = Number(value);
    if (value < 0) {
        value = Math.abs(value);
    }
    if (value > 100) {
        value = 100;
    }
    event.setValue({ value: `${value}`, onchange: true });
    field.finance_interest_interest_rate.setError({ valid: false, message: 'Error' });
}
global_finance_interest_interest_rate_onchange._delay = 0
```

### Instrucciones para el LLM

1. **Recibe como entrada:**
   - El código JS de la regla original.
   - Un mapeo de nombres antiguos a nuevos para entidades, campos y schemas.

2. **Analiza y actualiza:**
   - El nombre de la función, siguiendo la convención y usando los nuevos nombres.
   - Todas las referencias internas a campos y entidades en el código JS (por ejemplo, `field.<antiguo_nombre>` → `field.<nuevo_nombre>`).
   - Cualquier otro identificador relevante que dependa de los nombres antiguos.

3. **Mantén la lógica original:**
   - No cambies la lógica de validación o transformación, solo actualiza los nombres para que la regla funcione con el nuevo modelo de datos.

4. **Ejemplo de mapeo de nombres:**

   ```json
   {
     "account_payable_interest": "account_payable_interest",
     "rate": "interest_rate",
     "account_payable_interest_rate": "finance_interest_interest_rate"
   }
   ```

5. **Salida esperada:**
   - El código JS de la regla, listo para funcionar con los nuevos nombres de entidades y campos.
