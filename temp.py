{% block content %}
  <h2>Contact</h2>
  {% if success %}
    <p>Thank you for your message. We'll get back to you shortly.</p>
  {% else %}
    {% for message in form.name.errors %}
      <div class="flash">{{ message }}</div>
    {% endfor %}
    {% for message in form.email.errors %}
      <div class="flash">{{ message }}</div>
    {% endfor %}
    {% for message in form.subject.errors %}
      <div class="flash">{{ message }}</div>
    {% endfor %}
    {% for message in form.message.errors %}
      <div class="flash">{{ message }}</div>
    {% endfor %}
    <form action="{{ url_for('contact') }}" method=post>
      {{ form.hidden_tag() }}
      {{ form.name.label }}
      {{ form.name }}
      {{ form.email.label }}
      {{ form.email }}
      {{ form.subject.label }}
      {{ form.subject }}
      {{ form.message.label }}
      {{ form.message }}
      {{ form.submit }}
    </form>
  {% endif %}
{% endblock %}