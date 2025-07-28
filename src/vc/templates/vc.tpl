(set-logic LIA)

{%- for var in base_vars %}
(declare-const {{var}} Int)
(declare-const {{var}}! Int)
{%- endfor %}
{% for var in state_vars %}
(declare-const {{var}} Int)
{%- endfor %}

( define-fun inv-f( {% for var in base_vars %}( {{var}} Int ){% endfor %} ) bool
  {{inv}}
)
{% if pre_conditions %}
( define-fun pre-f ( {% for var in base_vars + state_vars %}( {{var}} Int ){% endfor %} ) bool
  ( and
    {%- for pre_condition in pre_conditions %}
    {{ pre_condition }}
    {%- endfor %}
  )
)

( assert ( not
	( =>
		( pre-f {% for var in base_vars + state_vars %} {{var}} {% endfor %})
		( inv-f {% for var in base_vars %}{{var}} {% endfor %} )
	)
))
{%- endif %}

{%- if trans_unchaged_state_conditions and trans_execution_conditions %}
( define-fun trans-f ( {% for var in base_vars + state_vars %}( {{var}} Int ){% endfor %} ) Bool
  ( or
    ( and
      {%- for condition in trans_unchaged_state_conditions %}
      {{ condition }}
      {%- endfor %}
    )
    ( and
      {%- for condition in trans_execution_conditions %}
      {{ condition }}
      {%- endfor %}
    )
  )
)

( assert ( not
	( =>
		( and
			( inv-f {% for var in base_vars %}{{var}} {% endfor %})
			( trans-f {% for var in base_vars + state_vars %}{{var}} {% endfor %})
		)
		( inv-f {% for var in base_vars %}{{var}}! {% endfor %})
	)
))
{%- endif %}

{%- if post_conditions and guard_conditions and loop_conditions %}
( define-fun post-f ( {% for var in base_vars + state_vars %}( {{var}} Int ){% endfor %} ) Bool
  ( or
    ( not
      ( and
        {%- for condition in guard_conditions %}
        {{condition}}
        {%- endfor %}
      )
    )
    ( not
      ( and
        {%- for condition in loop_conditions[:-1] %}
        {{ condition }}
        {%- endfor %}
        ( not {{loop_conditions[-1]}} )
        {%- for condition in post_conditions[:-1] %}
        {{ condition }}
        {%- endfor %}
        ( not {{post_conditions[-1]}} )
      )
    )
  )
)

( assert ( not
	( =>
		( inv-f {% for var in base_vars %}{{var}} {% endfor %})
		( post-f {% for var in base_vars + state_vars %}{{var}} {% endfor %})
	)
))
{%- endif %}
