function handleCall(req, res){
 
    console.log(
        "Teams Call Event:",
        JSON.stringify(req.body, null, 2)
    )
 
    res.sendStatus(200)
}
 
module. Exports={handleCall};