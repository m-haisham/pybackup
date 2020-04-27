/**
 * Create list item with text
 * @param {String} text text of item
 */
const createListItem = (text) => {
  var item = $("<li></li>").text(text).addClass("list-group-item selectable");

  $(item).click(function (e) {
    e.preventDefault();

    $(item).toggleClass("active");
  });

  return item;
};

/**
 * Add list item
 * @param {String} text item text
 */
const addListItem = (text) => {
  $(createListItem(text)).appendTo("#backups");
};

/**
 * reset backup list
 */
const resetList = () => {
  $(".list-group-item").remove();
};

const setDestination = (text) => {
  $("#des-input").val(text);
};

/**
 * @param {boolean} value new value
 */
const setOverwrite = (value) => {
  $("#overwrite-check").attr("checked", value);
};

/**
 * sets progress value
 * @param {number} value progress value between 0 and 100
 */
const setProgress = (value) => {
  $("#progress").css("width", `${value}%`);
};

/**
 * sets statusText
 * @param {String} text text to be set
 */
const setStatusText = (text) => {
  $("#status").text(text);
};

const backupDisabled = (value) => {
  $("#backup-btn").attr("disabled", value);
};

// add backup folder
$("#add-backup").click(function (e) {
  e.preventDefault();

  eel.addLocation();
});

// remove selected backup folders
$("#remove-backup").click(function (e) {
  e.preventDefault();

  $(".active").each((i, e) => {
    eel.removeLocation(e.innerText);
  });

  $(".active").remove();
});

// Destination picker
$("#des-button").click(function (e) {
  e.preventDefault();

  eel.askDestination()((path) => {
    setDestination(path);
  });
});

$("#overwrite-check").bind("change", function (e) {
  eel.setOverwrite(e.target.checked);
});

$("#backup-btn").click(function (e) {
  e.preventDefault();

  setProgress(0);
  setStatusText("");

  eel.backup();
});

// eel function exposure
eel.expose(addListItem, "add_list_item");
eel.expose(resetList, "reset_list");
eel.expose(setDestination, "set_destination");
eel.expose(setOverwrite, "set_overwrite");
eel.expose(setProgress, "set_progress");
eel.expose(setStatusText, "set_status_text");
eel.expose(backupDisabled, "backup_disabled");

// initialize eel
eel.init();
