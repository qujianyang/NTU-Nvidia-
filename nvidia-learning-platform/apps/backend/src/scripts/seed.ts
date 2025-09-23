import { PrismaClient } from '@prisma/client';
import coursesData from '../../../../packages/shared/src/data/courses.json';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Starting database seed...');

  // Clear existing data
  await prisma.message.deleteMany();
  await prisma.conversation.deleteMany();
  await prisma.userSavedPath.deleteMany();
  await prisma.userProgress.deleteMany();
  await prisma.userTargetSkill.deleteMany();
  await prisma.userSkill.deleteMany();
  await prisma.user.deleteMany();
  await prisma.pathCourse.deleteMany();
  await prisma.coursePrerequisite.deleteMany();
  await prisma.skill.deleteMany();
  await prisma.course.deleteMany();
  await prisma.learningPath.deleteMany();

  console.log('✅ Cleared existing data');

  // Create skills
  const skillSet = new Set<string>();
  coursesData.courses.forEach(course => {
    course.skills.forEach(skill => skillSet.add(skill));
  });

  const skills = await Promise.all(
    Array.from(skillSet).map(skillName =>
      prisma.skill.create({
        data: { name: skillName }
      })
    )
  );

  console.log(`✅ Created ${skills.length} skills`);

  // Create courses
  for (const course of coursesData.courses) {
    const createdCourse = await prisma.course.create({
      data: {
        id: course.id,
        title: course.title,
        duration: course.duration,
        price: course.price,
        type: course.type.toUpperCase().replace('-', '_') as any,
        category: course.category,
        difficulty: course.difficulty.toUpperCase() as any,
        certificate: course.certificate,
        digitalBadge: course.digitalBadge,
        role: course.role.toUpperCase() as any,
        skills: {
          connect: course.skills.map(skillName => ({
            name: skillName
          }))
        }
      }
    });
    console.log(`✅ Created course: ${createdCourse.title}`);
  }

  // Create prerequisites
  for (const course of coursesData.courses) {
    if (course.prerequisites && course.prerequisites.length > 0) {
      for (const prereqId of course.prerequisites) {
        await prisma.coursePrerequisite.create({
          data: {
            courseId: course.id,
            prerequisiteId: prereqId
          }
        });
      }
    }
  }

  console.log('✅ Created course prerequisites');

  // Create learning paths
  for (const path of coursesData.paths) {
    const createdPath = await prisma.learningPath.create({
      data: {
        id: path.id,
        title: path.title,
        role: path.role.toUpperCase() as any,
        category: path.category,
        description: path.description,
        totalDuration: path.totalDuration,
        totalCost: path.totalCost
      }
    });

    // Add courses to path
    for (let i = 0; i < path.courses.length; i++) {
      await prisma.pathCourse.create({
        data: {
          pathId: path.id,
          courseId: path.courses[i],
          order: i
        }
      });
    }

    console.log(`✅ Created learning path: ${createdPath.title}`);
  }

  // Create a demo user
  const demoUser = await prisma.user.create({
    data: {
      email: 'demo@nvidia-learning.com',
      name: 'Demo User',
      role: 'DEVELOPER',
      budget: 1000,
      timeAvailable: '20 hours/month',
      skills: {
        create: [
          { skillId: skills[0].id, level: 'INTERMEDIATE' },
          { skillId: skills[1].id, level: 'BEGINNER' }
        ]
      }
    }
  });

  console.log(`✅ Created demo user: ${demoUser.email}`);

  console.log('🎉 Database seed completed successfully!');
}

main()
  .catch((e) => {
    console.error('❌ Seed failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });