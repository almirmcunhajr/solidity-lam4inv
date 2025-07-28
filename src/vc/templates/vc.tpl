(set-logic LIA)

{%- for var in base_vars %}
(declare-const {{var[0]}} {{var[1]}})
(declare-const {{var[0]}}! {{var[1]}})
{%- endfor %}
{% for var in state_vars %}
(declare-const {{var[0]}} {{var[1]}})
{%- endfor %}

( define-fun inv-f( {{ base_parameters_def }} ) bool
{{ inv | indent(2, true) }}
)
{% if pre_conditions %}
( define-fun pre-f ( {{ base_parameters_def }} {{ state_parameters_def }} ) Bool
  ( and
    {%- for pre_condition in pre_conditions %}
    {{ pre_condition }}
    {%- endfor %}
  )
)

( assert ( not
	( =>
		( pre-f {{ base_parameters }} {{ state_parameters }} )
		( inv-f {{ base_parameters }} )
	)
))
{%- endif %}

{%- if trans_unchaged_state_conditions and trans_execution_conditions %}
( define-fun trans-f ( {{ base_parameters_def }} {{ state_parameters_def }} ) Bool
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
			( inv-f {{ base_parameters }} )
			( trans-f {{ base_parameters }} {{ state_parameters }} )
		)
		( inv-f {{ base_parameters }})
	)
))
{%- endif %}

{%- if post_conditions and guard_conditions and loop_conditions %}
( define-fun post-f ( {{ base_parameters_def }} {{ state_parameters_def }} ) Bool
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
		( inv-f  {{ base_parameters }} )
		( post-f {{ base_parameters }} {{ state_parameters }} )
	)
))
{%- endif %}
