import { useEffect, useMemo } from 'react';
import { useGameStore } from '../stores/useGameStore';

export const useSkills = () => {
  const skills = useGameStore((s) => s.skills);
  const talents = useGameStore((s) => s.talents);
  const tree = useGameStore((s) => s.tree);
  const fetchPlayerSkills = useGameStore((s) => s.fetchPlayerSkills);
  const fetchSkillsTree = useGameStore((s) => s.fetchSkillsTree);
  const setSkills = useGameStore((s) => s.setSkills);
  const setTalents = useGameStore((s) => s.setTalents);
  const getLevel = useGameStore((s) => s.getLevel);
  const getXp = useGameStore((s) => s.getXp);
  const hasTalent = useGameStore((s) => s.hasTalent);
  const getEffect = useGameStore((s) => s.getEffect);

  useEffect(() => {
    if (!skills?.length) fetchPlayerSkills();
    if (!tree?.length) fetchSkillsTree();
  }, [skills?.length, tree?.length, fetchPlayerSkills, fetchSkillsTree]);

  const craftingLevel = useMemo(() => getLevel('crafting'), [skills, getLevel]);
  const craftingXp = useMemo(() => getXp('crafting'), [skills, getXp]);
  const effects = useMemo(() => ({
    material_cost_reduction: getEffect('material_cost_reduction'),
    bonus_output_chance: getEffect('bonus_output_chance'),
    craft_speed_bonus: getEffect('craft_speed_bonus'),
  }), [talents, getEffect]);

  return {
    // state
    skills,
    talents,
    tree,
    // actions
    fetchPlayerSkills,
    fetchSkillsTree,
    setSkills,
    setTalents,
    // helpers
    getLevel,
    getXp,
    hasTalent,
    getEffect,
    // crafting convenience
    craftingLevel,
    craftingXp,
    effects,
  };
};
