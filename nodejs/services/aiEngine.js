const { GoogleGenerativeAI } = require("@google/generative-ai")

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)

async function generateQuestion(role){
    const model = genAI.getGenerativeModel({
        model: "gemini-2.0-flash"
    })

    const prompt = `Ask a technical interview question for ${role}`

    const result = await model.generateContent(prompt)

    return result.response.text()
}

module.exports={generateQuestion}