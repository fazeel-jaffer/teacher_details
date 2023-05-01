const form = document.getElementById('contact-form');
const name = document.getElementById('name');
const email = document.getElementById('email');
const message = document.getElementById('message');

form.addEventListener('submit', (event) => {
	event.preventDefault();
	checkInputs();
});

function checkInputs() {
	const nameValue = name.value.trim();
	const emailValue = email.value.trim();
	const messageValue = message.value.trim();

	if (nameValue === '') {
		setErrorFor(name, 'Name cannot be empty');
	} else {
		setSuccessFor(name);
	}

	if (emailValue === '') {
		setErrorFor(email, 'Email cannot be empty');
	} else if (!isEmail(emailValue)) {
		setErrorFor(email, 'Email is not valid');
	} else {
		setSuccessFor(email);
	}

	if (messageValue === '') {
		setErrorFor(message, 'Message cannot be empty');
	} else {
		setSuccessFor(message);
	}

	if (nameValue !== '' && emailValue !== '' && messageValue !== '') {
		form.submit();
	}
}

function setErrorFor(input, message) {
	const formGroup = input.parentElement;
	const errorMessage = formGroup.querySelector('.error-message');

	input.classList.add('error');
	errorMessage.innerText = message;
	formGroup.classList.add('error');
}

function setSuccessFor(input) {
	const formGroup = input.parentElement;

	input.classList.remove('error');
	formGroup.classList.remove('error');
}

function isEmail(email) {
	return /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email);
}
