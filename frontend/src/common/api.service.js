const axios = require("axios");

// necessary to post to django server
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

export { axios };
