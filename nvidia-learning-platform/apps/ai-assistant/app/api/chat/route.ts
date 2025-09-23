import { NextRequest, NextResponse } from 'next/server';
import { ChatOpenAI } from '@langchain/openai';
import { ConversationChain } from 'langchain/chains';
import { BufferMemory } from 'langchain/memory';
import { PromptTemplate } from '@langchain/core/prompts';
import coursesData from '../../../../packages/shared/src/data/courses.json';

const model = new ChatOpenAI({
  modelName: 'gpt-4',
  temperature: 0.7,
  openAIApiKey: process.env.OPENAI_API_KEY,
});

const memory = new BufferMemory();

const promptTemplate = new PromptTemplate({
  inputVariables: ['history', 'input'],
  template: `You are an AI assistant specialized in helping students navigate NVIDIA's learning pathways and courses.

Available courses and paths:
${JSON.stringify(coursesData, null, 2)}

Chat History:
{history}

Student Question: {input}

Please provide personalized recommendations based on:
1. The student's stated goals and interests
2. Their current skill level
3. Time availability and budget constraints
4. Prerequisites and recommended course sequences

Be conversational, helpful, and specific in your recommendations. Suggest 2-3 different learning paths when applicable.

Assistant Response:`,
});

export async function POST(req: NextRequest) {
  try {
    const { message, context } = await req.json();

    const chain = new ConversationChain({
      llm: model,
      memory,
      prompt: promptTemplate,
      verbose: true,
    });

    // Add context about user profile if available
    let enrichedMessage = message;
    if (context) {
      enrichedMessage = `
        User Context:
        - Role: ${context.role || 'Not specified'}
        - Current Skills: ${context.currentSkills?.join(', ') || 'None specified'}
        - Goals: ${context.goals || 'Not specified'}
        - Budget: ${context.budget || 'Not specified'}
        - Time Available: ${context.timeAvailable || 'Not specified'}

        User Question: ${message}
      `;
    }

    const response = await chain.call({ input: enrichedMessage });

    // Parse response to extract structured recommendations
    const recommendations = extractRecommendations(response.response);

    return NextResponse.json({
      message: response.response,
      recommendations,
    });
  } catch (error) {
    console.error('Chat API Error:', error);
    return NextResponse.json(
      { error: 'Failed to process chat message' },
      { status: 500 }
    );
  }
}

function extractRecommendations(response: string): any[] {
  const recommendations = [];

  // Extract course IDs mentioned in the response
  const courseIds = coursesData.courses.map(c => c.id);
  const pathIds = coursesData.paths.map(p => p.id);

  courseIds.forEach(id => {
    if (response.toLowerCase().includes(id.toLowerCase())) {
      const course = coursesData.courses.find(c => c.id === id);
      if (course) {
        recommendations.push({
          type: 'course',
          id: course.id,
          title: course.title,
          reason: 'Mentioned in recommendation'
        });
      }
    }
  });

  pathIds.forEach(id => {
    if (response.toLowerCase().includes(id.toLowerCase())) {
      const path = coursesData.paths.find(p => p.id === id);
      if (path) {
        recommendations.push({
          type: 'path',
          id: path.id,
          title: path.title,
          reason: 'Recommended learning path'
        });
      }
    }
  });

  return recommendations;
}