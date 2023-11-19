document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document
    .querySelector("#inbox")
    .addEventListener("click", () => load_mailbox("inbox"));
  document
    .querySelector("#sent")
    .addEventListener("click", () => load_mailbox("sent"));
  document
    .querySelector("#archived")
    .addEventListener("click", () => load_mailbox("archive"));
  document.querySelector("#compose").addEventListener("click", compose_email);

  // By default, load the inbox
  load_mailbox("inbox");
});

function sendmail() {
  fetch("/emails", {
    method: "POST",
    body: JSON.stringify({
      recipients: document.querySelector("#compose-recipients").value,
      subject: document.querySelector("#compose-subject").value,
      body: document.querySelector("#compose-body").value,
    }),
  });
}

function compose_email() {
  // Show compose view and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";
  document.querySelector("#display-view").style.display = "none";

  // Clear out composition fields
  document.querySelector("#compose-recipients").value = "";
  document.querySelector("#compose-subject").value = "";
  document.querySelector("#compose-body").value = "";
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#compose-view").style.display = "none";
  document.querySelector("#display-view").style.display = "none";

  // Show the mailbox name
  document.querySelector("#emails-view").innerHTML = `<h3>${
    mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
  }</h3>`;

  fetch("/emails/" + mailbox)
    .then((response) => response.json())
    .then((emails) => {
      // Print emails
      for (let i = 0; i < emails.length; i++) {
        const element = document.createElement("div");
        element.innerHTML =
          emails[i].sender +
          " " +
          emails[i].subject +
          " " +
          emails[i].timestamp;
        element.style.border = "solid 1px black";
        if (emails[i].read) {
          element.style.backgroundColor = "lightgray";
        } else {
          element.style.backgroundColor = "white";
        }
        if (mailbox != "sent") {
          const button = document.createElement("button");
          if (mailbox == "inbox") {
            button.textContent = "Archive";
          } else {
            button.textContent = "Unarchive";
          }
          button_click(button, emails[i].id);
          element.appendChild(button);

          // if (!button.dataset.clicked) {
          element.addEventListener("click", function () {
            document.querySelector("#display-view").style.display = "block";
            fetch("/emails/" + emails[i].id, {
              method: "PUT",
              body: JSON.stringify({
                read: true,
              }),
            });
            fetch("/emails/" + emails[i].id)
              .then((response) => response.json())
              .then((email) => {
                // Print email
                mail_content(email);
              });
          });
          // }
        }
        document.querySelector("#emails-view").append(element);
      }
    });
}

function button_click(button, email_id) {
  button.addEventListener("click", function () {
    fetch("/emails/" + email_id, {
      method: "PUT",
      body: JSON.stringify({
        archived: button.textContent == "Archive",
      }),
    });
    button.dataset.clicked = "true";
    load_mailbox("inbox");
  });
}

function mail_content(email) {
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "none";
  const from = document.createElement("div"),
    to = document.createElement("div"),
    subject = document.createElement("div"),
    body = document.createElement("div"),
    timestamp = document.createElement("div"),
    reply = document.createElement("button"),
    ruler = document.createElement("hr");
  from.innerHTML = "<b>From: </b>" + email.sender;
  to.innerHTML = "<b>To: </b>" + email.recipients;
  subject.innerHTML = "<b>Subject: </b>" + email.subject;
  timestamp.innerHTML = "<b>Timestamp: </b>" + email.timestamp;
  reply.textContent = "Reply";

  reply.addEventListener("click", function () {
    compose_email();
    document.querySelector("#compose-recipients").value = email.sender;
    if (email.subject.includes("Re:")) {
      document.querySelector("#compose-subject").value = email.subject;
    } else {
      document.querySelector("#compose-subject").value = "Re: " + email.subject;
    }
    document.querySelector("#compose-body").value =
      "On " + email.timestamp + " " + email.sender + " wrote:" + email.body;
  });

  ruler.style.border = "solid 0.25px lightgray";
  body.innerHTML = email.body;
  document
    .querySelector("#display-view")
    .append(from, to, subject, timestamp, reply, ruler, body);
}
