document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("receipt-form");
    const messagesContainer = document.getElementById("form-messages");
    const submitBtn = form.querySelector(".btn-submit");

    document.querySelectorAll("[data-clear-input]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = document.getElementById(button.getAttribute("data-clear-input"));
            if (!input) return;
            input.value = "";
            input.focus();
        });
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        clearErrors();
        clearMessages();
        setSubmitting(true);

        const formData = new FormData(form);
        const url = form.action || window.location.href;
        const csrfToken = formData.get("csrfmiddlewaretoken");

        fetch(url, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrfToken,
            },
            body: formData,
        })
            .then((response) => response.json().then((data) => ({ response, data })))
            .then(({ response, data }) => {
                setSubmitting(false);

                if (response.ok && data.status === "ok") {
                    showSuccess(data.message);
                    form.reset();
                    return;
                }

                if (!response.ok && data.status === "error" && data.errors) {
                    renderErrors(data.errors);
                    return;
                }

                showMessage(
                    gettext("Произошла непредвиденная ошибка. Попробуйте ещё раз."),
                    "alert-error"
                );
            })
            .catch(() => {
                setSubmitting(false);
                showMessage(
                    gettext("Ошибка сети. Проверьте соединение и попробуйте ещё раз."),
                    "alert-error"
                );
            });
    });


    function clearErrors() {
        form.querySelectorAll(".field--error").forEach((f) => f.classList.remove("field--error"));
        form.querySelectorAll(".field-error").forEach((el) => el.classList.add("hidden"));
        form.querySelectorAll(".form-input--error").forEach((input) => input.classList.remove("form-input--error"));
        form.querySelectorAll(".field-required").forEach((el) => el && el.remove());
    }

    function clearMessages() {
        messagesContainer.innerHTML = "";
    }

    function showMessage(text, cssClass) {
        const div = document.createElement("div");
        div.className = "alert " + cssClass;
        div.textContent = text;
        messagesContainer.appendChild(div);
    }

    function showSuccess(text) {
        showMessage(text, "alert-success");
    }

    function setSubmitting(loading) {
        submitBtn.disabled = loading;
        submitBtn.textContent = loading
            ? gettext("Отправка…")
            : gettext("Загрузить");
    }

    function renderErrors(errors) {
        if (errors.__all__) {
            errors.__all__.forEach((msg) => showMessage(msg, "alert-error"));
        }

        Object.keys(errors).forEach((fieldName) => {
            if (fieldName === "__all__") return;
            const fieldBlock = document.getElementById("field-" + fieldName);
            const errorContainer = fieldBlock && fieldBlock.querySelector(".field-error");
            const input = fieldBlock && fieldBlock.querySelector(".form-input, input, select");

            if (!fieldBlock || !errorContainer || !errors[fieldName].length) return;

            fieldBlock.classList.add("field--error");

            if (input) {
                input.classList.add("form-input--error");
            }

            const wrap = fieldBlock.querySelector(".form-input-wrap");
            if (input && input.hasAttribute("required") && wrap) {
                const asterisk = document.createElement("img");
                asterisk.className = "field-required";
                asterisk.src = "/static/core/img/icon-error-asterisk.svg";
                asterisk.width = 8;
                asterisk.height = 8;
                asterisk.alt = "";
                wrap.appendChild(asterisk);
            }

            const bubbleText = errorContainer.querySelector(".field-error-bubble span");
            if (bubbleText) {
                bubbleText.textContent = errors[fieldName][0];
            }

            errorContainer.classList.remove("hidden");
        });
    }

});
