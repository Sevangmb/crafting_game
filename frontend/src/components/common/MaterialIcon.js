import React from 'react';

/**
 * Component to display material icon - either emoji or image
 */
const MaterialIcon = ({ icon, size = 24, style = {} }) => {
    // Check if icon is an image URL
    const isImage = icon && (icon.startsWith('http') || icon.startsWith('/media'));

    if (isImage) {
        return (
            <img
                src={icon}
                alt="icon"
                style={{
                    width: size,
                    height: size,
                    objectFit: 'contain',
                    ...style
                }}
            />
        );
    }

    // Display as emoji/text
    return <span style={{ fontSize: size, ...style }}>{icon}</span>;
};

export default MaterialIcon;
