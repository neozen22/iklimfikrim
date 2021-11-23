const express = require('express');
const router = express.Router();



router.get("/articles/:id", async (req, res) => {
    const article_id = req.params.id;
    console.log(article_id);
})

//listen to port 4000
router.listen(4000, () => {
    console.log("listening on port 4000");
});