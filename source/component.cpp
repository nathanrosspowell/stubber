//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Component.cpp Authored by Nathan Ross Powell.
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#ifndef __HEADER_COMPONENT__
#define __HEADER_COMPONENT__

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Definition of Component< typename T, int N = 10 >.
template< typename T, int N = 10 >
class Component : public BaseComponent, public Counter< Component >
{
// Public functions.
public:
    void init();
    void update();
    dllexport Int theId( Bool lookip, Id theId ) const;

// Protected functions.
protected:
    Bool initPro();

// Private functions.
private:
    void deleteAll();
    void type( const TypeId& type );

// Protected members.
protected:
    std::map< Names*, Id > m_hash;

// Private members.
private:
    const Id& m_id;
    std::vector< Component* > m_components;

};

#endif __HEADER_COMPONENT__
