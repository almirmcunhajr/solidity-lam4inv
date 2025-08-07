(set-logic LIA)

{%- set base_parameters_def_list = [] -%}
{%- for var in base_vars -%}
  {%- set _ = base_parameters_def_list.append('({} {})'.format(var[0], var[1])) -%}
{%- endfor -%}
{%- set base_parameters_def = base_parameters_def_list | join(' ') -%}

{%- set primed_parameters_def_list = [] -%}
{%- for var in base_vars -%}
  {%- set _ = primed_parameters_def_list.append('({}! {})'.format(var[0], var[1])) -%}
{%- endfor -%}
{%- set primed_parameters_def = primed_parameters_def_list | join(' ') -%}

{%- set state_parameters_def_list = [] -%}
{%- for var in state_vars -%}
  {%- set _ = state_parameters_def_list.append('({} {})'.format(var[0], var[1])) -%}
{%- endfor -%}
{%- set state_parameters_def = state_parameters_def_list | join(' ') -%}

{%- set base_parameters = base_vars | map(attribute=0) | join(' ') -%}

{%- set primed_parameters_list = [] -%}
{%- for var in base_vars -%}
  {%- set _ = primed_parameters_list.append(var[0] ~ '!') -%}
{%- endfor -%}
{%- set primed_parameters = primed_parameters_list | join(' ') -%}

{%- set state_parameters = state_vars | map(attribute=0) | join(' ') -%}

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
(check-sat)
{%- endif %}

{%- if trans_execution_conditions %}
( define-fun trans-f ( {{ base_parameters_def }} {{ primed_parameters_def }} {{ state_parameters_def }} ) Bool
  ( or
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
			( trans-f {{ base_parameters }} {{ primed_parameters }} {{ state_parameters }} )
		)
		( inv-f {% for var in base_vars %}{{var[0]}}! {% endfor %})
	)
))
(check-sat)
{%- endif %}

{%- if post_conditions %}
( define-fun post-f ( {{ base_parameters_def }} {{ state_parameters_def }} ) Bool
  ( or
    ( not
      ( and
        ( not {{loop_condition}} )
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
(check-sat)
{%- endif %}
