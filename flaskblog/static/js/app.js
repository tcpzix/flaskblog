// document.getElementById('todo-form').addEventListener('onsubmit', addTodo);

//like post function with 'onclick' attribute in img element
const likePost = function (postid) {
  let likeCount = document.getElementById(postid);
  // Cheke post for befor liked
  if (sessionStorage.getItem(`postid${postid}`) === "liked") {
    console.log("This Post was Liked befor!!!");
  } else {
    // make a get request for liked post
    const http = new easyHTTP();
    http.get(`/like/${postid}`, function (err, response) {
      if (err) {
        console.log(err);
      } else {
        // change like count span text
        likeCount.textContent = response;
        // save liked post in sessionstorage for stop double liking
        sessionStorage.setItem(`postid${postid}`, "liked");
      }
    });
  }
};

// convert Post Date to Jalali
const faDate = function (elemid, date, showdatetag) {
  // get the small tag that show date
  let rawDate = document.getElementById(showdatetag + elemid);
  // convert date and change persian number to latin
  let persianDate = new Date(date)
    .toLocaleDateString("fa-IR")
    .replace(/([۰-۹])/g, (token) =>
      String.fromCharCode(token.charCodeAt(0) - 1728)
    );
  // add date text to small tag
  rawDate.textContent = persianDate;
};

// Truncate Postcard Text
const truncate = function (element, max, after) {
  if (!element || !max) return;
  let content = element.textContent.trim();
  content = content.split(" ").slice(0, max);
  content = content.join(" ") + (after ? after : " ");
  element.textContent = content;
};

// Submit post comment
const addComment = function (postid) {
  // grab comment field
  const nameField = document.querySelector(".comment-name");
  const emailField = document.querySelector(".comment-email");
  const messageField = document.querySelector(".comment-message");

  // check user input email with regex
  const checkMail = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;

  // chekc field for white space with(trim) and not empty with length
  if (
    nameField.value.trim().length == 0 ||
    messageField.value.trim().length == 0 ||
    checkMail.test(emailField.value) == false
  ) {
    alert(
      "لطفا تمام فیلد هارو پر کرده و از درست بودن ساختار ایمیل مطمئن باشید"
    );
  } else {
    // make a dic with form field value
    data = {
      name: nameField.value,
      email: emailField.value,
      message: messageField.value,
    };

    // maek and post request
    const http = new easyHTTP();
    http.post(window.origin + `/comment/${postid}`, data, function (err, res) {
      if (err) {
        console.log(err);
      } else {
        console.log(res);

        // get show comment ul and inject new comment to it
        const commentUl = document.querySelector(".show-comment");
        const newLi = `<li class="collection-item grey lighten-3 blue-grey-text right-align">
                <span id="highlight" class="title">${nameField.value}</span>
                <p>${messageField.value}</p>
                </li>`;
        commentUl.innerHTML += newLi;

        // clear comment form field
        nameField.value = "";
        emailField.value = "";
        messageField.value = "";
      }
    });
  }
};

// Add toto task
const addTodo = function (e) {
  // select task ul
  const todoList = document.querySelector(".todos");
  // Get user input
  let userInput = document.querySelector("#todo");

  const newTask = userInput.value;

  // Post Req to server
  const http = new easyHTTP();
  http.post(window.origin + "/addtodo", newTask, function (err, res) {
    if (err) {
      console.log(err);
    } else {
      console.log(res);
      // insert new task in dom
      const output = `<li class="collection-item">
            <div>${newTask}
            <a href="#!" class="secondary-content delete">
                <i class="material-icons">close</i>
            </a>
            </div>
            </li>`;
      todoList.innerHTML += output;
    }
  });
  userInput.value = "";
  // disable defult submit
  e.preventDefault();
};

// Delete Todo Task
const todoDel = document.querySelectorAll(".delete");
for (let a of todoDel) {
  a.addEventListener("click", (e) => {
    // Remove li (task)
    let taskId = a.id;
    const http = new easyHTTP();
    http.post(window.origin + "/deltodo", taskId, function (err, res) {
      if (err) {
        console.log(err);
      } else {
        console.log(res);
        a.parentElement.parentElement.remove();
      }
    });

    e.preventDefault();
  });
}

const newPost = function (e) {
  // Get Post Form data
  const title = document.getElementById("post-title").value;
  const category = document.getElementById("post-category").value;
  const content = CKEDITOR.instances["post-content"].getData();
  console.log("submiting.....");
  data = {
    title: title,
    category: category,
    content: content,
  };
  console.log(data);
  const http = new easyHTTP();
  http.post(window.origin + "/post/new", data, function (err, res) {
    if (err) {
      console.log(err);
    } else {
      console.log(res);
    }
    // Hard reload page
    location.reload(true);
  });

  e.preventDefault();
};

const delPost = function (e, postid) {
  console.log(postid);
  const http = new easyHTTP();

  http.post(window.origin + "/delpost", postid, function (err, res) {
    if (err) {
      console.log(err);
    } else {
      console.log(res);
    }
    location.reload(true);
  });

  e.preventDefault();
};

const editPost = function (postid) {
  const http = new easyHTTP();
  // retrive post data
  http.get(window.origin + `/editpost/${postid}`, (err, res) => {
    if (err) {
      console.log(err);
    } else {
      // server response with post data
      const data = JSON.parse(res);
      // split title and content
      const title = data.title;
      const content = data.content;
      const category = data.category;
      // input current post data into form
      document.getElementById("edit-title").value = title;
      CKEDITOR.instances["edit-post"].setData(content);
      // this tag is a proxy for hold post id for using it in next function (updatePost)
      document.getElementById("postid-proxy").setAttribute("post-id", postid);
      console.log(res);
    }
  });
};

const updatePost = function (e) {
  const postId = document
    .getElementById("postid-proxy")
    .getAttribute("post-id");

  const title = document.getElementById("edit-title").value;
  const content = CKEDITOR.instances["edit-post"].getData();
  const category = document.getElementById("edit-category").value;
  console.log("submiting.....");
  data = {
    title: title,
    category: category,
    content: content,
  };
  const http = new easyHTTP();
  http.post(window.origin + `/editpost/${postId}`, data, (err, res) => {
    if (err) {
      console.log(err);
    } else {
      console.log(res);
    }

    location.reload(true);
  });

  e.preventDefault();
};

const addCat = function (e) {
  userInput = document.getElementById("category-title");

  const http = new easyHTTP();

  http.post(window.origin + "/addcategory", userInput.value, (err, res) => {
    if (err) {
      console.log(err);
    } else {
      console.log(res);
    }
    // Hard reload page
    location.reload(true);
  });

  e.preventDefault();
};

const delCat = function (catid) {
  const http = new easyHTTP();

  http.post(window.origin + "/del-category", catid, (err, res) => {
    if (err) {
      console.log(err);
    } else {
      console.log(res);
      location.reload(true);
    }
  });
};

const editCat = function (catid) {
  const http = new easyHTTP();
  http.get(window.origin + `/edit-category/${catid}`, (err, res) => {
    if (err) {
      console.log(err);
    } else {
      const data = JSON.parse(res);
      document.getElementById("editcat-title").value = data;
      document.getElementById("catid-proxy").setAttribute("cat-id", catid);
    }
  });
};

const updateCat = function () {
  catid = document.getElementById("catid-proxy").getAttribute("cat-id");
  const userInput = document.getElementById("editcat-title").value;
  const http = new easyHTTP();
  http.post(
    window.origin + `/edit-category/${catid}`,
    userInput,
    (err, res) => {
      if (err) {
        console.log(err);
      } else {
        console.log(res);
      }
      location.reload(true);
    }
  );
};

const addUser = function (e) {
  let name = document.getElementById("user-name");
  let email = document.getElementById("user-email");
  let password = document.getElementById("user-password");
  let password2 = document.getElementById("user-password2");
  const checkMail = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
  if (
    password.value != password2.value ||
    name.value == "" ||
    checkMail.test(email.value) == false
  ) {
    alert(
      "Please input all field and right email and same password for two field"
    );
  } else {
    data = {
      name: name.value,
      email: email.value,
      password: password.value,
    };
    const http = new easyHTTP();
    http.post(window.origin + "/adduser", data, (err, res) => {
      if (err) {
        console.log(err);
      } else {
        console.log(res);
      }
      location.reload(true);
    });
  }
};

const changePass = function (e) {
  let oldPass = document.getElementById("old-password");
  let newPass = document.getElementById("new-password");
  let newPass2 = document.getElementById("new-password2");
  errorView = document.getElementById("changepass-errors");

  if (newPass.value === newPass2.value) {
    data = {
      oldpass: oldPass.value,
      newpass: newPass.value,
    };
    const http = new easyHTTP();
    http.post(window.origin + "/changepass", data, (err, res) => {
      if (err) {
        console.log(err);
      } else {
        errorView.textContent = res;
      }
    });
  } else {
    errorView.textContent = "new pass and confirm not equel!";
  }

  e.preventDefault();
};

const delUser = function (userid) {
  const http = new easyHTTP();

  http.post(window.origin + "/deluser", userid, (err, res) => {
    if (err) {
      console.log(err);
    } else {
      console.log(res);
    }
    location.reload(true);
  });
};
